import sys
import logging
import traceback
from src import app
import asyncio


def exception_logging(exctype, value, tb):
    write_val = {
        'exception_type': str(exctype),
        'trace': str(traceback.format_tb(tb)),
        'message': value
    }

    logging.exception(str(write_val))


async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        # initialize logging
        logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
        sys.excepthook = exception_logging

        import splunk.entity as splunk_entity_module
        import splunk.rest as splunk_rest_module
        raw_payload = sys.stdin.read()
        return sys.exit(await app.run(raw_payload, splunk_entity_module, splunk_rest_module))
    elif len(sys.argv) == 2 and sys.argv[1] == "--local":
        raw_payload = open("test.json").read()
        return sys.exit(await app.run(raw_payload, None, None, ["--local"]))

if __name__ == '__main__':
    asyncio.run(main())
