import os
from pathlib import Path

from .file import PytestFileGen


class PytestProjectGen:
    def __init__(self, project_folder_path, pytest_folder_path=None):
        self.project_folder_path: Path = Path(project_folder_path)
        self.pytest_folder_path: Path = Path(pytest_folder_path)

    def generate_pytest_files(self):
        for dirpath, _, filenames in os.walk(self.project_folder_path):
            for filename in filenames:
                if filename.endswith(".py") and not filename.startswith("__init__"):
                    self._generate_pytest_file(dirpath, filename)
        self._create_init_files()

    def _create_init_files(self):
        for dirpath, _, _ in os.walk(self.pytest_folder_path):
            init_file = os.path.join(dirpath, "__init__.py")
            open(init_file, "a").close()

    def _generate_pytest_file(self, dir_path, file_name):
        source_file_path = Path(dir_path).joinpath(file_name)
        rel_path = os.path.relpath(source_file_path.parent, self.project_folder_path)
        pytest_file_path = self.pytest_folder_path.joinpath(rel_path).joinpath("test_" + file_name)

        file_gen: PytestFileGen = PytestFileGen(
            source_file_path=source_file_path,
            pytest_file_path=pytest_file_path,
            project_parent_path=self.project_folder_path.parent
        )
        file_gen.generate_pytest_file()
