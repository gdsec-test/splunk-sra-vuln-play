import unittest
from unittest.mock import MagicMock
from . import handle_paramaterized_function_asserts


class TestInit(unittest.TestCase):
    def test_handle_paramaterized_function_asserts_with(self):
        class Test():
            def foo_func(self):
                pass

            def bar_func(self):
                pass

            def baz_func(self):
                pass

        foo = Test()

        foo.foo_func = MagicMock(return_value=True)
        foo.foo_func(True)
        case_one_exp = {"called": {"foo_func": (True,)}, }
        handle_paramaterized_function_asserts(foo, case_one_exp)

        case_two_exp = {"called": {
            "bar_func": {
                "positional": "qux",
                "kwargs": {"quux": "quuz"}
            }}}
        foo.bar_func = MagicMock()
        foo.bar_func("qux", quux="quuz")
        handle_paramaterized_function_asserts(foo, case_two_exp)

        case_three_exp = {"not_called": ["baz_func"]}
        foo.baz_func = MagicMock()
        handle_paramaterized_function_asserts(foo, case_two_exp)
