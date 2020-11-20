import asyncio
import json
import re
import aiohttp
import requests
from datetime import datetime
from dateutil.parser import parse as parse_date
from .Utils import string_0_1_to_bool
from .constants import APPNAMESPACE, STATE_COLLECTION_NAME, BASE_DOMAIN, \
    SERVICENOW_REQUEST_HEADERS, TABLE_FIELDS, SNOW_TIME_FORMAT, \
    PARAMETER_REGEX

MAX_URL_LENGTH = 7000

SYSPARAM_FIELDS = [
    "name", "sys_id",
    # "u_patching_group.manager.sys_id",
    # "sys_class_name", "ip_address"
    # "assignment_group.name", "u_patching_group.name", "u_patching_group.manager.name", "u_patching"
    # "u_patching_group.manager.email",
    # "u_patching_group.u_business_service_rollup.u_product_line.u_business_unit.name"
]
ROOT_CAUSE = "Security.Vulnerability"
VULNERABILITY_TYPE = "Vuln"


class ServiceNow():
    def __init__(self, credentials, configuration, initialize=True):
        # SNOW service account credentials
        self._credentials = credentials
        # self._results = results   # The "results" of the Alert Action
        self._config = configuration   # The "configuration" of the Alert Action

        self._url = None
        self._data = {}  # Data that will be posted to Service-Now

        if initialize:
            self.initialize()

    def initialize(self):
        self._url = self._construct_url()  # Service-Now URL

    def _construct_url(self):
        """
        Constructs the URL used for the request (between dev and prod
        Service-Now instances).
        """
        if self._config.get("environment") == "prod":
            domain = BASE_DOMAIN
        else:
            domain = BASE_DOMAIN + 'dev'

        return domain + '.service-now.com/api/now/table'

    def construct_ci_base_url(self):
        sysparm_fields_text = "%2C".join(SYSPARAM_FIELDS)

        base_url = f"{self._url}/cmdb_ci_hardware?sysparm_fields={sysparm_fields_text}&sysparm_query=install_statusNOT%20IN7%2C8%5E"

        return base_url

    def fetch_manager(self, serial_number):
        url = f"{self._url}/cmdb_ci_hardware?sysparm_fields=u_patching_group.manager.sys_id&sysparm_query=install_statusNOT%20IN7%2C8%5Eserial_number%3D{serial_number}"
        response = requests.get(
            url=url,
            auth=self._credentials
        )

        if response.status_code == 200:
            return response.json()['result'][0].get('u_patching_group.manager.sys_id')

        return None

    def fetch_cis(self, serial_numbers):
        base_url = self.construct_ci_base_url()
        cis = []
        while len(serial_numbers) is not 0:
            url = base_url
            while len(serial_numbers) is not 0 and len(url) < MAX_URL_LENGTH:
                url += f"serial_number%3D{serial_numbers.pop()}%5ENQ"
            cis.extend(self._fetch_cis(url))

        return cis

    def _fetch_cis(self, url):
        response = requests.get(
            url=url,
            auth=self._credentials
        )

        if response.status_code == 200:
            return response.json()['result']

        return []

    def get_ticket(self, sys_id):
        url = f"{self._url}/problem?sysparm_query=sys_id%3D{sys_id}&sysparm_fields=state&sysparm_limit=1"
        response = requests.get(
            url=url,
            auth=self._credentials
        )

        if 200 <= response.status_code and response.status_code < 299:
            return response.json()["result"][0]
        elif response == 404:
            return None

        raise RuntimeError(json.dumps({
            "Status:": response.status_code,
            "Headers:": str(response.headers),
            "Error Response:": response.json()
        }))

    def construct_post_data(self, cis, service_team, assigned_user):
        data = {
            'short_description': self._config['title'],
            'description': self._config['description'],
            'assignment_group': service_team,
            'u_root_cause': ROOT_CAUSE,
            'u_vulnerability_type': VULNERABILITY_TYPE,
            'u_vulnerability_criticality': self._config['criticality'],
            'urgency': self._config['urgency'],
            'impact': self._config['impact'],
            'u_problem_notes': 'Affected CIs\n'+"\n".join(cis)
        }

        if assigned_user is not None:
            data['assigned_to'] = assigned_user
        if self._config.get('custom_tag'):
            data["u_custom_tag"] = self._config.get('custom_tag')

        return data

    def create_ticket(self, data):
        """
        Sends the data to Service-Now and checks for a 200 status code.
        """
        response = requests.post(url=f"{self._url}/problem",
                                 auth=self._credentials,
                                 headers=SERVICENOW_REQUEST_HEADERS,
                                 data=json.dumps(data))

        if 200 <= response.status_code and response.status_code <= 299:
            sys_id = response.json()['result']['sys_id']
            return sys_id
        else:
            raise RuntimeError(json.dumps({
                "Status:": response.status_code,
                "Headers:": str(response.headers),
                "Error Response:": response.json()
            }))

    # https://stackoverflow.com/questions/51699817/python-async-post-requests
    async def attach_cis(self, sys_id, cis):
        bad_cis = []

        async def do_post(session, ci):
            async with session.post(
                f"{self._url}/task_ci?sysparm_fields=ci_item",
                data=json.dumps({"task": sys_id, "ci_item": ci}),
            ) as response:
                if response.status < 200 or 299 < response.status:
                    bad_cis.append(ci)

        headers = SERVICENOW_REQUEST_HEADERS
        auth = aiohttp.BasicAuth(*self._credentials)
        async with aiohttp.ClientSession(headers=headers, auth=auth) as session:
            tasks = [do_post(session, ci) for ci in cis]
            await asyncio.gather(*tasks)

        return bad_cis

    def update_ticket(self, sys_id, cis):
        data = {"u_problem_notes": 'New Affected CIs\n'+"\n".join(cis)}
        self.put(sys_id, data)

    def put(self, sys_id, data):
        """
        Sends the data to Service-Now and checks for a 200 status code.
        """
        response = requests.put(url=self._url + "/problem/{}".format(sys_id),
                                auth=self._credentials,
                                headers=SERVICENOW_REQUEST_HEADERS,
                                data=json.dumps(data))

        if 200 > response.status_code or response.status_code > 299:
            raise RuntimeError(json.dumps({
                "Status:": response.status_code,
                "Headers:": str(response.headers),
                "Error Response:": response.json()
            }))
