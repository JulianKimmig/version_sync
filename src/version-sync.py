#!/usr/bin/env python3
import argparse
import json
import sys

# Use built-in tomllib if available (Python 3.11+), otherwise fall back to third-party 'toml'
try:
    import tomllib
except ImportError:
    import toml as tomllib

def get_pyproject_version(path: str) -> str:
    """Read the version from the given pyproject.toml file.
    
    Expects the version under [tool.poetry]:
        [tool.poetry]
        version = "1.0.0"
    """
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        version = data["tool"]["poetry"]["version"]
    except KeyError:
        print(f"Error: Could not locate version in '{path}' under [tool.poetry].", file=sys.stderr)
        sys.exit(1)
    return version

def get_packagejson_version(path: str) -> str:
    """Read the version from the given package.json file."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        version = data["version"]
    except KeyError:
        print(f"Error: Could not find the 'version' key in '{path}'.", file=sys.stderr)
        sys.exit(1)
    return version

def main():
    parser = argparse.ArgumentParser(
        description="Check version consistency between pyproject.toml and package.json."
    )
    parser.add_argument(
        "--pyproject",
        default="pyproject.toml",
        help="Path to the pyproject.toml file (default: pyproject.toml)."
    )
    parser.add_argument(
        "--package",
        default="package.json",
        help="Path to the package.json file (default: package.json)."
    )
    args = parser.parse_args()

    py_version = get_pyproject_version(args.pyproject)
    node_version = get_packagejson_version(args.package)

    if py_version != node_version:
        print(
            "Version mismatch detected:\n"
            f"  - {args.pyproject} version: '{py_version}'\n"
            f"  - {args.package} version:   '{node_version}'",
            file=sys.stderr
        )
        sys.exit(1)
    else:
        print(f"Versions match: '{py_version}'")
        sys.exit(0)

if __name__ == "__main__":
    main()
