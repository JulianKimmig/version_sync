import json
import sys
from packaging.version import Version


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


def sync_package_json_version(path: str, version: Version) -> None:
    """Update the 'version' key in a package.json file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)
    data["version"] = str(version)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    except Exception as e:
        print(f"Error writing {path}: {e}", file=sys.stderr)
        sys.exit(1)
