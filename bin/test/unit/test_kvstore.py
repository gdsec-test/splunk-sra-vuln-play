import unittest
from unittest.mock import MagicMock
from ..src.constants import APPNAMESPACE
from . import handle_paramaterized_function_asserts, mock_splunk_entity_module, mock_splunk_rest_module

from ..src import KVStore
# from ..src.constants import TABLE_FIELDS


class TestServiceNow(unittest.TestCase):
    def test_get_service_account_credentials(self):
        session_key = "foo"
        kv = KVStore(session_key, mock_splunk_entity_module,
                     mock_splunk_rest_module)

        returns = {"r": {"username": "bar", "clear_password": "baz"}}
        mock_getEntities = MagicMock(return_value=returns)
        mock_splunk_entity_module.getEntities = mock_getEntities

        call_exp = {
            "called": {
                "getEntities": {
                    "positional": ['admin', 'passwords'],
                    "kwargs": {"namespace": APPNAMESPACE, "owner": "nobody", "sessionKey": session_key}
                }
            }
        }
        exp = (returns['r']['username'], returns['r']['clear_password'])
        got = kv.get_service_account_credentials()

        handle_paramaterized_function_asserts(
            mock_splunk_entity_module, call_exp)
        self.assertEqual(got, exp)

    def test_raise_if_collection_not_exist(self):
        cases = [
            # Case 1 - 201
            (
                "Case 1",
                [{"status": "201"}, ''],
                {
                    "called": {
                        "create_collection": (),
                        "define_new_collection_schema": ()
                    }
                }
            ),
            # Case 2 - 409
            (
                "Case 2",
                [{"status": "409"}, ''],
                # [{"status": "409"}, '{"messages":"error"}'],
                {
                    "called": {
                        "create_collection": (),
                    },
                    "not_called": ["define_new_collection_schema"]
                }
            )
        ]

        for (case, values, exp) in cases:
            kv = KVStore(None, mock_splunk_entity_module,
                         mock_splunk_rest_module)
            kv.create_collection = MagicMock(
                return_value=values)
            kv.define_new_collection_schema = MagicMock()

            kv.raise_if_collection_not_exist()

            handle_paramaterized_function_asserts(kv, exp)

            print(case + " ... pass!")
