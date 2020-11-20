import unittest
from dateutil.parser import parse as parse_date
from unittest.mock import MagicMock
from ..src import Utils
# from . import handle_paramaterized_function_asserts


class TestUtils(unittest.TestCase):
    def test_string_0_1_to_bool(self):
        self.assertEqual(Utils.string_0_1_to_bool("1"), True)
        self.assertEqual(Utils.string_0_1_to_bool("0"), False)
