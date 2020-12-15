import hashlib
import json
import requests

APPNAMESPACE = "splunk_sra_vuln_play"

STATE_COLLECTION_NAME = "gd_" + APPNAMESPACE

COLLECTION_SCHEMA = {
    "field.ticket_sys_id": "string"
}


class KVStore():
    def __init__(self, session_key, splunk_entity_module, splunk_rest_module):
        self.session_key = session_key
        self.entity = splunk_entity_module
        self.rest = splunk_rest_module

    def get_service_account_credentials(self):
        """
        Access the credentials in /servicesNS/nobody/app_name/admin/passwords
        2-Write-a-python-script-that-uses-credentials
        From: https://dev.splunk.com/enterprise/docs/developapps/setuppage/setupxmlexamples/
        """
        try:
            # list all credentials
            entities = self.entity.getEntities(
                ['admin', 'passwords'],
                namespace=APPNAMESPACE,
                owner='nobody',
                sessionKey=self.session_key
            )
        except Exception as e:
            raise Exception(
                f"Could not get {APPNAMESPACE} credentials from splunk. Error: {str(e)}")

        # return first set of credentials
        for c in entities.values():
            return c['username'], c['clear_password']

        # raise Exception("No credentials have been found")

    def raise_if_collection_not_exist(self):
        [headers, bodyRaw] = self.create_collection()
        status = headers["status"]
        if status == "201":
            # successfully created
            self.define_new_collection_schema()
        elif status != "409":
            # does not already exists
            body = json.loads(bodyRaw)
            exceptMessage = f"Failed to make collection. Status: {status}. Messages:"

            i = 0
            for message in body["messages"]:
                i += 1
                exceptMessage += f"\n{i}. {message['text']}"

            raise Exception(exceptMessage)

    def create_collection(self):
        collection_name = {"name": STATE_COLLECTION_NAME}
        return self.rest.simpleRequest(
            "/servicesNS/nobody/search/storage/collections/config?output_mode=json",
            postargs=collection_name,
            sessionKey=self.session_key
        )

    def define_new_collection_schema(self):
        return self.rest.simpleRequest(
            "/servicesNS/nobody/search/storage/collections/config?output_mode=json",
            postargs=COLLECTION_SCHEMA,
            sessionKey=self.session_key
        )

    @staticmethod
    def construct_key(key):
        meta = b"{}".format(key)
        return hashlib.sha256(meta).hexdigest()

    def get_state(self, key):
        try:
            uri = f"/servicesNS/nobody/search/storage/collections/data/{STATE_COLLECTION_NAME}/{key}?output_mode=json"
            [headers, bodyRaw] = self.rest.simpleRequest(
                uri,
                sessionKey=self.session_key
            )
            status = headers["status"]
            body = json.loads(bodyRaw)

            if status == "200":
                return body
        except Exception as err:
            if err.statusCode == 404:
                return None
            else:
                raise err

        exceptMessage = f"Unknown status. Status: {status}. Messages:"

        i = 0
        for message in body["messages"]:
            i += 1
            exceptMessage += f"\n{i}. {message['text']}"

        raise Exception(exceptMessage)

    def post_state(self, key, ticket_sys_id, is_new):
        if is_new:
            post_url = f"/servicesNS/nobody/search/storage/collections/data/{STATE_COLLECTION_NAME}?output_mode=json"
        else:
            post_url = f"/servicesNS/nobody/search/storage/collections/data/{STATE_COLLECTION_NAME}/{key}?output_mode=json"
        state = {
            "_key": key,
            "ticket_sys_id": ticket_sys_id
        }
        [headers, bodyRaw] = self.rest.simpleRequest(
            post_url,
            jsonargs=json.dumps(state),
            sessionKey=self.session_key,
        )
        status = headers["status"]

        if status != "200" and status != "201":
            body = json.loads(bodyRaw)
            exceptMessage = f"Failed to update collection. Status: {status}. Messages:"

            i = 0
            for message in body["messages"]:
                i += 1
                exceptMessage += f"\n{i}. {message['text']}"

            raise Exception(exceptMessage)
