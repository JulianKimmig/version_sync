#!/usr/bin/env python3
import argparse
from packaging.version import Version
import sys
from typing import Dict
from pathlib import Path
from .package_json import get_packagejson_version, sync_package_json_version
from .pyproject_toml import get_pyproject_version, sync_pyproject_version
from .pyfile import get_pyfile_version, sync_pyfile_version
# Use built-in tomllib if available (Python 3.11+), otherwise fall back to third-party 'toml'


def parse_versions(args):
    files = list(args.files)
    pyvars = args.py_vars.split(";")
    versions = {}
    for file in files:
        path = Path(file).absolute()
        if file.name == "pyproject.toml":
            version = get_pyproject_version(path)
        elif file.name == "package.json":
            version = get_packagejson_version(path)
        elif file.suffix == ".py":
            version = get_pyfile_version(path, pyvars)
        else:
            print(f"Error: Unsupported file type '{file.suffix}'.", file=sys.stderr)
            sys.exit(1)

        if version is None:
            print(f"Error: Could not find version in '{file}'.", file=sys.stderr)
            sys.exit(1)

        versions[file] = Version(version)

    return versions


def sync_versions(parsed_versions: Dict[Path, Version], highest_version: Version, args):
    for file, ver_obj in parsed_versions.items():
        if ver_obj != highest_version:
            if file.name == "package.json":
                sync_package_json_version(file, highest_version)
            elif file.name == "pyproject.toml":
                sync_pyproject_version(file, highest_version)
            elif file.suffix == ".py":
                sync_pyfile_version(file, args.py_vars.split(";"), highest_version)


def main():
    parser = argparse.ArgumentParser(
        description="Check version consistency between pyproject.toml and package.json."
    )

    parser.add_argument(
        "--py-vars",
        help="variable names that used to find versions in python files, separated by ';'.",
        default="version;VERSION;__version__;__VERSION__",
        type=str,
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help="If provided, update all files to the highest version found.",
    )

    # example: --py-vars version;VERSION;__version__;__VERSION__

    # all other args are files
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Paths to the files to check (default: pyproject.toml and package.json).",
    )

    args = parser.parse_args()
    # print(list(args.files))
    parsed_versions = parse_versions(args)
    if len(parsed_versions) == 0:
        print("No versions found. Exiting.")
        sys.exit(1)
    print("Versions found:")
    for file, version in parsed_versions.items():
        print(f"  - {file}: '{version}'")

    # Determine the highest version
    highest_version = max(parsed_versions.values())

    if args.sync:
        # Sync all files to the highest version.
        sync_versions(parsed_versions, highest_version, args)
        print("Synchronization complete. All file versions set to", highest_version)
        sys.exit(0)
    else:
        # Without syncing, just check for consistency.
        if len(set(parsed_versions.values())) != 1:
            print(
                "Error: Versions are not consistent across all files.", file=sys.stderr
            )
            for file, ver in parsed_versions.items():
                print(f"  - {file}: '{ver}'")
            sys.exit(1)
        else:
            print("Versions match:", highest_version)
            sys.exit(0)


if __name__ == "__main__":
    main()
