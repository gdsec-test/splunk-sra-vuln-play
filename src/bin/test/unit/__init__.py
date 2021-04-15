def handle_paramaterized_function_asserts(c, exp):
    if "called" in exp:
        for func_name, values in exp["called"].items():
            func = getattr(c, func_name)
            if isinstance(values, dict):
                func.assert_called_with(
                    values['positional'], **values['kwargs'])
            else:
                func.assert_called_with(*values)

    if "not_called" in exp:
        for func_name in exp["not_called"]:
            getattr(c, func_name).assert_not_called()


class mock_splunk_entity_module():
    def getEntities(self):
        pass


class mock_splunk_rest_module():
    pass
