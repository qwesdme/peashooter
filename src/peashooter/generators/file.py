import ast
import os
from pathlib import Path

from helpers.data_classes import Class, Function, Param, Methods


class PytestFileGen:
    def __init__(self, source_file_path: Path, pytest_file_path: Path, project_parent_path: Path | None = None):
        self.source_file_path: Path = source_file_path
        self.pytest_file_path: Path = pytest_file_path
        self.project_parent_path: Path = project_parent_path
        self.classes: list[Class] = []
        self.functions: list[Function] = []

    def _parse_source_file(self):
        with open(self.source_file_path, "r") as source:
            tree = ast.parse(source.read())

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                self._handle_function_node(node)
            elif isinstance(node, ast.ClassDef):
                self._handle_class_node(node)

    def _handle_class_node(self, node):
        methods = []
        # noinspection PyTypeChecker
        for sub_node in ast.iter_child_nodes(node):
            if isinstance(sub_node, ast.FunctionDef):
                # noinspection PyUnresolvedReferences
                method_params = self._method_params(sub_node)
                if sub_node.name == "__init__" or not sub_node.name.startswith("__"):
                    methods.append(Methods(sub_node.name, method_params))
        if methods:
            self.classes.append(Class(node.name, methods))

    def _handle_function_node(self, node):
        # noinspection PyUnresolvedReferences,PyTypeChecker
        function_params = [Param(arg.arg, ast.unparse(arg.annotation) if arg.annotation else None) for arg in
                           node.args.args]
        self.functions.append(Function(node.name, function_params))

    @staticmethod
    def _method_params(sub_node):
        return [Param(arg.arg, ast.unparse(arg.annotation) if arg.annotation else None)
                for arg in sub_node.args.args
                if arg.arg != "self" and not arg.arg.startswith('*')
                ]

    def _write_imports(self, pytest_file):
        pytest_file.write("import pytest\n\n")
        class_and_function_names_str = self._class_and_function_names_str()
        pytest_file.write("# noinspection PyProtectedMember\n")
        if self.project_parent_path is None:
            pytest_file.write(f"from {self.source_file_path.stem} import ({class_and_function_names_str})\n")
        else:
            import_path = os.path.relpath(
                os.path.splitext(self.source_file_path)[0], self.project_parent_path
            ).replace(os.path.sep, ".")
            pytest_file.write(f"from {import_path} import ({class_and_function_names_str})\n")

    def _class_and_function_names_str(self):
        class_names: list[str] = [class_.name for class_ in self.classes]
        function_names: list[str] = [function.name for function in self.functions]
        class_and_function_names = class_names + function_names
        class_and_function_names_str = ",\n    ".join(class_and_function_names)
        if len(class_and_function_names) > 1:
            class_and_function_names_str = f"\n    {class_and_function_names_str}\n"
        return class_and_function_names_str

    def _write_pytest_functions(self, pytest_file):
        functions_count = len(self.functions)
        for i, func in enumerate(self.functions, 1):
            func.write_pytest_function(pytest_file)
            if i < functions_count:
                pytest_file.write('\n\n')

    def _write_pytest_classes(self, pytest_file):
        classes_count = len(self.classes)
        for i, cls in enumerate(self.classes, 1):
            cls.write_test_class(pytest_file)
            if i < classes_count:
                pytest_file.write('\n\n')

    def generate_pytest_file(self, ):
        self._parse_source_file()
        has_class = len(self.classes) > 0
        has_function = len(self.functions) > 0

        if has_class or has_function:
            os.makedirs(self.pytest_file_path.parent, exist_ok=True)

            with open(self.pytest_file_path, "w") as pytest_file:
                self._write_imports(pytest_file)
                if has_class:
                    pytest_file.write('\n\n')
                    self._write_pytest_classes(pytest_file)
                if has_function:
                    pytest_file.write('\n\n')
                    self._write_pytest_functions(pytest_file)
