import traceback
import json
import logging
import asyncio
import sys
import os

sys.path.insert(0, os.environ['SPLUNK_HOME'] +
                '/etc/apps/splunk-sra-vuln-play/lib')


REQUIRED_CONFIG_FIELDS = [
    'environment',
    'ticket_title',
    'ticket_description',
    'ticket_impact',
    'ticket_urgency',
    'ticket_criticality',
    'ticket_assign_to_manager',
]


def exception_logging(exctype, value, tb):
    write_val = {
        'exception_type': str(exctype),
        'trace': str(traceback.format_tb(tb)),
        'message': value
    }

    logging.exception(str(write_val))


def config_is_valid(_config):
    """
    Checks that all values for REQUIRED_CONFIG_FIELDS in the alert are set in the
    alert action.
    """
    for c in REQUIRED_CONFIG_FIELDS:
        value = _config.get(c)
        if value is None or value == "":
            logging.exception(
                "'{}' is a required setup parameter, but its value is None.".format(c))
            return False

    return True


async def main():
    from src import app

    splunk_entity_module = None
    splunk_rest_module = None
    flags = []
    payload = None

    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        # initialize logging
        logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
        sys.excepthook = exception_logging

        import splunk.entity as splunk_entity_module
        import splunk.rest as splunk_rest_module
        payload = json.loads(sys.stdin.read())
    elif sys.argv[1] == "--local":
        with open(sys.argv[2]) as file:
            raw_payload = file.read()
            payload = json.loads(raw_payload)
        flags = sys.argv

    if payload is not None and not config_is_valid(payload['configuration']):
        return sys.exit(2)

    return sys.exit(await app.run(payload, splunk_entity_module, splunk_rest_module, flags))


if __name__ == '__main__':
    asyncio.run(main())
