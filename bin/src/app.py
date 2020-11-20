# from __future__ import print_function

import os
import csv
import json
import gzip
import shutil
from operator import itemgetter

from .ServiceNow import ServiceNow
from .KVStore import KVStore
from .Utils import string_0_1_to_bool

from .constants import MANDATORY_CONFIG, TABLE_FIELDS

VULN_PLAY_FIELD_NAME = "Vuln_Play_Name"
SERIAL_FIELD_NAME = "Serial"
SERVICE_TEAM_FIELD_NAME = "Svc_Team"
EVENT_FIELDS = [
    VULN_PLAY_FIELD_NAME, SERIAL_FIELD_NAME, SERVICE_TEAM_FIELD_NAME
]
MAX_CI_MANAGER_TRY = 10


async def run(raw_payload, splunk_entity_module, splunk_rest_module, flags=[]):
    # extra event meta ( session_key, configuration, results_file )
    session_key, configuration, results_file_path = read_in_payload(
        raw_payload)

    # load results from file
    headers, results = load_results(results_file_path)

    is_running_local = "--local" in flags
    kv_store = None
    if is_running_local:
        credentials = (os.environ.get("SNOW_USERNAME"),
                       os.environ.get("SNOW_PASSWORD"))
    else:
        # initialize service now and kv store clients
        kv_store = KVStore(
            session_key, splunk_entity_module, splunk_rest_module
        )
        kv_store.raise_if_collection_not_exist()
        credentials = kv_store.get_service_account_credentials()

    service_now = ServiceNow(credentials, configuration)

    # parse results into relevant structure
    # - get field index
    # - parse from arr into below structure
    """{ svc_team: { manager_id, vuln_play: [...serial] } }"""
    header_map = construct_header_map(headers, EVENT_FIELDS)
    serial_map = construct_serial_map(header_map, results)

    # fetch cis <- SNOW
    ci_map = construct_ci_map(service_now, serial_map, configuration)

    # create / update ticket
    await cut_tickets(service_now, kv_store, session_key,
                      configuration, ci_map, is_running_local)

    return 0


def read_in_payload(raw_payload):
    payload = json.loads(raw_payload)
    session_key, configuration, results_file_path = itemgetter(
        "session_key", "configuration", "results_file"
    )(payload)

    return session_key, configuration, results_file_path


def load_results(file_path):
    with gzip.open(file_path, 'rt', newline="\n") as f_in:
        results = csv.reader(f_in.readlines(), delimiter=",")
        results = list(results)
        headers = results.pop(0)
        return headers, results


def construct_header_map(csv_headers, fields):
    header_map = {}
    for field in fields:
        for i in range(len(csv_headers)):
            if csv_headers[i] == field:
                header_map[field] = i
    return header_map


def construct_serial_map(header_map, results):
    serial_idx = header_map[SERIAL_FIELD_NAME]
    vuln_play_idx = header_map[VULN_PLAY_FIELD_NAME]
    service_team_idx = header_map[SERVICE_TEAM_FIELD_NAME]

    ci_map = {}
    for result in results:
        serial_number = result[serial_idx]
        vuln_play = result[vuln_play_idx]
        service_team = result[service_team_idx]

        upsert_result_into_ci_map(
            ci_map, serial_number, vuln_play, service_team)

    return ci_map


def upsert_result_into_ci_map(ci_map, serial_number, vuln_play, service_team):
    team_vulns = ci_map.get(service_team)
    if team_vulns is not None:
        ci_arr = team_vulns.get(vuln_play)
        if ci_arr is None:
            team_vulns[vuln_play] = [serial_number]
        else:
            ci_arr.append(serial_number)
    else:
        ci_map[service_team] = {vuln_play: [serial_number]}


def construct_ci_map(service_now, serial_map, configuration):
    ci_map = {}
    for service_team, vulns in serial_map.items():
        for vuln_play, serial_numbers in vulns.items():
            ci_map[service_team] = ci_map.get(service_team, {})
            team = ci_map[service_team]
            team['manager'] = get_manager(
                configuration, service_now, serial_numbers)
            team['vuln_plays'] = team.get('vuln_plays', {})
            team['vuln_plays'][vuln_play] = service_now.fetch_cis(
                serial_numbers)

    return ci_map


def get_manager(configuration, service_now, serial_numbers):
    manager = None
    if string_0_1_to_bool(configuration.get('assign_manager')):
        i = 0
        while manager == None and i < len(serial_numbers) and i < MAX_CI_MANAGER_TRY:
            manager = service_now.fetch_manager(serial_numbers[i])
            i += 1

    return manager


async def cut_tickets(service_now, kv_store, session_key, configuration, ci_map, is_running_local):
    for service_team, team in ci_map.items():
        manager, vulns = itemgetter("manager", "vuln_plays")(team)
        for vuln_play, cis in vulns.items():
            sys_id = await upsert_ticket(
                service_now, kv_store,
                session_key, configuration,
                service_team, vuln_play, cis,
                manager, is_running_local
            )
            print(sys_id)
            # update_kv_store(service_team, vuln_play, sys_id)
    # kv_store.post_state(key, sys_id, state is None)


async def upsert_ticket(service_now, kv_store, session_key, configuration, service_team, vuln_play_value, cis, manager, is_running_local):
    # check splunk for existing sys_id (team + vuln play)
    sys_id = None
    if not is_running_local:
        kv_store_key = kv_store.construct_key(service_team + vuln_play_value)
        sys_id = kv_store.get_state(kv_store_key)

    ci_names = []
    ci_ids = []
    for ci_item in cis:
        ci_names.append(ci_item['name'])
        ci_ids.append(ci_item['sys_id'])

    if sys_id is not None and is_ticket_open(service_now, sys_id):
        service_now.update_ticket(sys_id, ci_names)
    else:
        data = service_now.construct_post_data(
            ci_names, service_team, manager)
        sys_id = service_now.create_ticket(data)

    await service_now.attach_cis(sys_id, ci_ids)

    return sys_id


def is_ticket_open(service_now, sys_id):
    ticket = service_now.get_ticket(sys_id)
    return ticket != None and ticket['state'] == "1"


def update_kv_store(service_team, vuln_play, sys_id):
    """TODO"""
    return None
