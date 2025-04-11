import ast
import sys
from typing import List


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
                    # For Python < 3.8, string literals are ast.Str.
                    if isinstance(node.value, ast.Str):
                        return node.value.s
                    # For Python 3.8+, string literals are represented as ast.Constant.
                    elif isinstance(node.value, ast.Constant) and isinstance(
                        node.value.value, str
                    ):
                        return node.value.value

    print(f"Error: No version assignment found in '{path}'.", file=sys.stderr)
    sys.exit(1)
