import ast
import sys
from typing import List
from pathlib import Path
import re


def get_pyfile_version(path: str, pyvars: List[str]) -> str:
    """
    Extract the version string from a Python file by searching for assignment
    statements to one of the given variable names.

    Args:
        path (str): The file path to the Python file.
        pyvars (List[str]): A list of variable names (e.g. ["__version__", "version", "VERSION"])
                            that might hold the version string.

    Returns:
        str: The version string if found.

    Exits:
        Exits with an error message if the file cannot be parsed or no version is found.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        print(f"Error parsing '{path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Walk through all nodes in the AST
    for node in ast.walk(tree):
        # Look for assignment nodes
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in pyvars:
                    return node.value.value

    print(f"Error: No version assignment found in '{path}'.", file=sys.stderr)
    sys.exit(1)


def sync_pyfile_version(path: Path, pyvars: List[str], new_version: str) -> None:
    """
    Update the version in a Python file by searching for assignments to one of the provided
    version variable names and replacing the value with the new version.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Construct a regex pattern to catch assignment to any of the candidate version variables.
    pattern = re.compile(
        r"^(\s*("
        + "|".join(re.escape(var) for var in pyvars)
        + r')\s*=\s*)([\'"])(.*?)([\'"])(.*)$'
    )
    new_lines = []
    found = False
    for line in lines:
        m = pattern.match(line)
        if m:
            prefix = m.group(1)
            quote = m.group(3)
            suffix = m.group(6)
            new_line = f"{prefix}{quote}{new_version}{quote}{suffix}\n"
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)

    if not found:
        print(
            f"Warning: No version assignment found in {path} to update.",
            file=sys.stderr,
        )

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"Error writing {path}: {e}", file=sys.stderr)
        sys.exit(1)
