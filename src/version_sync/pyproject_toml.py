import toml
import sys
from pathlib import Path
from packaging.version import Version


def get_pyproject_version(path: Path) -> str:
    try:
        with open(path, "r") as f:
            # Use tomllib if available (Python 3.11+), otherwise fall back to third-party 'toml'
            data = f.read()
        data = toml.loads(data)
    except FileNotFoundError:
        print(f"Error: '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        # poetry
        return data["tool"]["poetry"]["version"]
    except KeyError:
        pass

    try:
        # setuptools
        return data["project"]["version"]
    except KeyError:
        pass

    print(f"Error: Could not find the 'version' key in '{path}'.", file=sys.stderr)
    sys.exit(1)


def sync_pyproject_version(path: Path, new_version: Version) -> None:
    """Update the version key in a pyproject.toml file under [tool.poetry] or [project]."""

    new_version = str(new_version)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = toml.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)

    updated = False
    if (
        "tool" in data
        and "poetry" in data["tool"]
        and "version" in data["tool"]["poetry"]
    ):
        data["tool"]["poetry"]["version"] = new_version
        updated = True
    if "project" in data and "version" in data["project"]:
        data["project"]["version"] = new_version
        updated = True
    if not updated:
        print(f"Warning: No version field found in {path} to update.", file=sys.stderr)

    try:
        with open(path, "w", encoding="utf-8") as f:
            toml.dump(data, f)
    except Exception as e:
        print(f"Error writing {path}: {e}", file=sys.stderr)
        sys.exit(1)
