import unittest
from unittest.mock import MagicMock
from dateutil.parser import parse as parse_date
from . import handle_paramaterized_function_asserts

from ..src import ServiceNow
from ..src.constants import TABLE_FIELDS


class TestServiceNow(unittest.TestCase):
    def test_construct_from_results(self):
        print("\nRunning: test_construct_from_results")

    def test_initialize(self):
        r = ServiceNow({}, {}, {})
        exp = "foo"
        r._construct_url = MagicMock(return_value=exp)
        r.initialize()
        self.assertEqual(r._url, exp)

    def test_set_url(self):
        print("\nRunning: test_set_url")
        parameters = [
            # Case 1 - environment is not prod
            (
                "Case 1",
                {
                    "environment": "",
                    "table": "sometable"
                },
                "https://godaddydev.service-now.com/api/now/table/sometable"
            ),
            # Case 2 - environment is 'prod'
            (
                "Case 2",
                {
                    "environment": "prod",
                    "table": "sometable"
                },
                "https://godaddy.service-now.com/api/now/table/sometable"
            )
        ]

        for (case, _config, exp) in parameters:
            r = ServiceNow({}, {}, {})
            r._config = _config

            got = r._construct_url()
            self.assertEqual(got, exp)
            print(case + " ... pass!")

    def test_extract_config(self):
        print("\nRunning: test_extract_config")

        config = {}
        # {
        #     _config,
        #     _table_fields,
        #     exp functions
        # }
        parameters = [
            # Case 1: test empty
            # Even though this isn't expected, it will test at the same time
            # all cases being empty
            (
                "Case 1",
                {
                    "called": {
                        "_set_data_field": ("u_state", None),
                        "_set_data_replace": ("u_detection_method", None, "ticket_detection_method"),
                        "_set_data_datetime": ("u_event_time", None),
                        "_set_data_boolean": ("u_dsr", None)
                    }
                }
            ),
        ]

        for (case, exp) in parameters:
            r = ServiceNow({}, {}, config)

            r._set_data_field = MagicMock()
            r._set_data_replace = MagicMock()
            r._set_data_datetime = MagicMock()
            r._set_data_boolean = MagicMock()

            r._extract_config()

            handle_paramaterized_function_asserts(r, exp)

            print(case + " ... pass!")

    # def test_data(self):
    #     print("\nRunning: test_data")
    #     r = ServiceNow()
    #     r._set_data_field("k", "v")

    #     exp = {"k": "v"}

    #     self.assertEqual(r._data, exp)

    #     print("Case ... pass!")

    def test_data_replace(self):
        print("\nRunning: test_data_replace")
        parameters = [
            # Case 1 - with value -
            # should call _set_data_field and _replace_params
            (
                "Case 1",
                {"snow_field": "field", "value": "val", "config_field": "_"},
                {
                    "called": {
                        "_set_data_field": ("field", "_replace_params.returns"),
                        "_replace_params": ("val",)
                    }
                }
            ),
            # Case 2 - empty string -
            # should not call _set_data_field and _replace_params
            (
                "Case 2",
                {"snow_field": "field", "value": "", "config_field": "_"},
                {
                    "not_called": ["_set_data_field", "_replace_params"]
                }
            ),
            # Case 3 - with None -
            # should not call _set_data_field and _replace_params
            (
                "Case 3",
                {"snow_field": "field", "value": None, "config_field": "_"},
                {
                    "not_called": ["_set_data_field", "_replace_params"]
                }
            ),
        ]

        for (case, values, exp) in parameters:
            r = ServiceNow({}, {}, {})
            r._set_data_field = MagicMock()
            r._replace_params = MagicMock(
                return_value="_replace_params.returns")

            r._set_data_replace(**values)

            handle_paramaterized_function_asserts(r, exp)

            print(case + " ... pass!")

    def test_set_data_datetime(self):
        print("\nRunning: test_set_data_datetime")
        some_time = "2006-01-02T15:04:05"
        some_time_in_snow = "2006-01-02 15:04:05"
        _results = {"_time": 1136214245.000}
        parameters = [
            # Case 1 - with 'now' - value = 'now'
            (
                "Case 1",
                {"snow_field": "field", "value": "now",
                    "now": parse_date("2006-01-02T15:04:05")},
                {
                    "called": {
                        "_set_data_field": ("field",
                                            some_time_in_snow)
                    },
                    "not_called": ["_extract_field"]
                }
            ),
            # Case 2 - with value - value = '_time'
            (
                "Case 2",
                {"snow_field": "field", "value": "_time", "now": "0"},
                {
                    "called": {
                        "_set_data_field": ("field", some_time_in_snow)
                    },
                    "not_called": ["_extract_field"]
                }
            ),
            # Case 2 - with value - value = *
            (
                "Case 2",
                {"snow_field": "field", "value": "some.value", "now": "0"},
                {
                    "called": {
                        "_extract_field": ("some.value",),
                        "_set_data_field": ("field", some_time_in_snow)
                    },
                }
            ),
            # Case 3 - with none - value = None
            (
                "Case 3",
                {"snow_field": "field", "value": None, "now": "0"},
                {
                    "not_called": ["_set_data_field", "_extract_field"]

                }
            ),
            # Case 4 - with empty string - value = ''
            (
                "Case 4",
                {"snow_field": "field", "value": "", "now": "0"},
                {
                    "not_called": ["_set_data_field", "_extract_field"]

                }
            ),
        ]

        for (case, values, exp) in parameters:
            r = ServiceNow({}, {}, {})
            r._results = _results
            r._set_data_field = MagicMock()
            r._extract_field = MagicMock(return_value=some_time)

            r._set_data_datetime(**values)

            handle_paramaterized_function_asserts(r, exp)

            print(case + " ... pass!")

    def test_replace_params(self):
        print("\nRunning: test_replace_params")

        _replace_params_returns = "returned"
        parameters = [
            # Case 1 - No regex match & no newlinw -
            # string without "{{}}" and \n
            (
                "Case 1",
                {"string": "Some string."},
                {
                    "not_called": ["_replace_next_param"],
                    "got": "Some string."
                }
            ),
            # Case 2 - No regex match & newlinw -
            # string without "{{}}"
            (
                "Case 2",
                {"string": "Some\\nstring."},
                {
                    "not_called": ["_replace_next_param"],
                    "got": "Some\nstring."
                }
            ),
            # Case 3 - regex match & newlinw -
            # string with "{{}}"
            (
                "Case 3",
                {"string": "{{some.string}}"},
                {
                    "called": {"_replace_next_param": ("{{some.string}}",)},
                    "got": _replace_params_returns
                }
            )
        ]

        for (case, values, exp) in parameters:
            r = ServiceNow({}, {}, {})
            r._replace_next_param = MagicMock(
                return_value=_replace_params_returns)

            got = r._replace_params(**values)

            handle_paramaterized_function_asserts(r, exp)
            self.assertEqual(got, exp["got"])

            print(case + " ... pass!")

    def test_replace_next_param(self):
        print("\nRunning: test_replace_next_param")
        parameters = [
            # Case 1 - results is string
            (
                "Case 1",
                {"field_one": "value1"},
                {"param_string": "some {{field_one}}"},
                {
                    "_parse_param": "field_one",
                    "_extract_field": "_"
                },
                {
                    "called": {"_parse_param": ("some {{field_one}}",)},
                    "not_called": ["_extract_field"],
                    "got": "some value1"
                },
            ),
            # Case 2 - results is dict
            (
                "Case 2",
                {"field_one": {"foo": "bar"}},
                {"param_string": "some {{field_one}}"},
                {
                    "_parse_param": "field_one",
                    "_extract_field": "_"
                },
                {
                    "called": {"_parse_param": ("some {{field_one}}",)},
                    "not_called": ["_extract_field"],
                    "got": 'some {"foo": "bar"}'
                },
            ),
        ]

        for (case, _results, values, returns, exp) in parameters:
            r = ServiceNow({}, {}, {})
            r._results = _results
            r._parse_param = MagicMock(
                return_value=returns["_parse_param"])
            r._extract_field = MagicMock(
                return_value=returns["_extract_field"])

            got = r._replace_next_param(**values)

            handle_paramaterized_function_asserts(r, exp)

            self.assertEqual(got, exp["got"])

            print(case + " ... pass!")

    def test_parse_param(self):
        print("\nRunning: test_parse_param")
        parameters = [
            (
                "Case 1",
                {"param_string": "{{some.string}}"},
                "some.string"
            ),
            (
                "Case 2",
                {"param_string": "a {{some.string}} b"},
                "some.string"
            ),
            (
                "Case 3",
                {"param_string": "a {{some}} b {{string}} c"},
                "some"
            ),
        ]

        for (case, values, exp) in parameters:
            r = ServiceNow({}, {}, {})

            got = r._parse_param(**values)

            self.assertEqual(got, exp)

            print(case + " ... pass!")

    def test_extract_field(self):
        print("\nRunning: test_extract_field")
        _results = {
            "case_one": "value1",
            "case": {
                "two": "value2",
                "three": {"value": "3"}
            }
        }

        parameters = [
            # Case 1 - No '.'
            (
                "Case 1",
                {"field_path": "case_one"},
                "value1"
            ),
            # Case 2 - One '.'
            (
                "Case 2",
                {"field_path": "case.two"},
                "value2"
            ),
            # Case 3 - Multiple '.'
            (
                "Case 3",
                {"field_path": "case.three.value"},
                "3"
            ),
        ]

        for (case, values, exp) in parameters:
            r = ServiceNow({}, {}, {})
            r._results = _results

            got = r._extract_field(**values)

            self.assertEqual(got, exp)

            print(case + " ... pass!")


# if __name__ == '__main__':
    # unittest.main()

    # parameters = []
    # for (case, values, exp) in parameters:
    #     got = func(**values)

    #     handle_paramaterized_function_asserts(r, exp)

    #     self.assertEqual(got, exp)

    #     print(case + " ... pass!")
