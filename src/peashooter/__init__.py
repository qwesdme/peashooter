import argparse

from generators.project import PytestProjectGen

# Parse the command-line arguments
parser = argparse.ArgumentParser(description="Generate pytest test files for a Python project")
parser.add_argument("project_directory", type=str, help="Path to the project directory")
args = parser.parse_args()

# Generate test files for the specified project directory
ppg = PytestProjectGen(args.project_directory, "output/tests")
ppg.generate_pytest_files()
