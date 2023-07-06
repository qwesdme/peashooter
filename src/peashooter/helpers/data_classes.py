import re

from helpers.statics import *


class Param:
    def __init__(self, name: str, type_: str):
        self.name: str = name
        self.type: str = type_


class Function:
    def __init__(self, name, params: list[Param] | None = None):
        self.name = name
        self.params: list[Param] = [] if params is None else params

    def write_pytest_function(self, pytest_file):
        has_args = len(self.params) > 0
        arg_note = f"  {ARG_NOTE}" if has_args else ""
        pytest_file.write(f"{PYTEST_NEW_TEST_SKIP_DECORATOR}\n")
        if has_args:
            param_names = ", ".join([param.name for param in self.params])
            pytest_file.write(
                f"@pytest.mark.parametrize('{param_names}', [])  # add parameter values\n"
                f"def test_{self.name}({param_names}):\n"
            )
        else:
            pytest_file.write(f"def test_{self.name}():\n")
        pytest_file.write(
            f"    {TEST_CONTENT_NOTE}\n"
            f"    _result = {self.name}(){arg_note}\n"
            f"    {ASSERT_RESULT_NOTE}\n"
        )


class Methods(Function):
    ...


class Class:
    def __init__(self, name, methods: list[Methods] | None = None):
        self.name: str = name
        self.methods: list[Methods] = [] if methods is None else methods
        self.fixture_name: str = self._fixture_name()

    def _fixture_name(self) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self.name).lower() + "_fixture"

    def test_class_def(self) -> str:
        return f"class Test{self.name}:\n"

    def fixture_content(self) -> str:
        init_params_str = self._init_params_str()
        return f"    @pytest.fixture\n" \
               f"    def {self.fixture_name}(self) -> {self.name}:\n" \
               f"        # TODO: complete this fixture content\n" \
               f"        return {self.name}({init_params_str})\n\n"

    def _init_params_str(self):
        init_params_str: str | None = None

        for method in self.methods:
            if method.name == "__init__":
                init_params_str = ",\n            ".join(f"{param.name}=None" for param in method.params)
                if len(method.params) > 1:
                    init_params_str = f"\n            {init_params_str}\n        "
                break

        if init_params_str is None:
            init_params_str = ""
        return init_params_str

    def write_test_class(self, pytest_file):
        pytest_file.write(self.test_class_def())
        pytest_file.write(self.fixture_content())
        self.write_test_methods(pytest_file)

    def write_test_methods(self, pytest_file):
        methods_count = len(self.methods)
        for i, method in enumerate(self.methods, 1):
            if method.params and method.params[0].name == "self":
                method.params.pop(0)

            has_args = len(method.params) > 0
            pytest_file.write(f"    {PYTEST_NEW_TEST_SKIP_DECORATOR}\n")
            if has_args:
                param_names = ", ".join([param.name for param in method.params])
                pytest_file.write(
                    f"    @pytest.mark.parametrize('{param_names}', [])  # add parameter values\n"
                    f"    def test_{method.name}(self, {self.fixture_name}, {param_names}):\n"
                )
            else:
                pytest_file.write(
                    f"    def test_{method.name}(self, {self.fixture_name}):\n"
                )

            arg_note = f"  {ARG_NOTE}" if has_args else ""
            method_call_str = self.name if method.name == "__init__" else f"{self.fixture_name}.{method.name}"

            pytest_file.write(
                f"        {TEST_CONTENT_NOTE}\n"
                f"        _result = {method_call_str}(){arg_note}\n"
                f"        {ASSERT_RESULT_NOTE}\n"
            )

            if i < methods_count:
                pytest_file.write('\n')
