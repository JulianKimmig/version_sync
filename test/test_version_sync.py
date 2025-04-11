import json
import re
import textwrap
import pytest
from pathlib import Path
from packaging.version import Version

# Import the functions from your package.
from version_sync.package_json import (
    get_packagejson_version,
    sync_package_json_version,
)
from version_sync.pyproject_toml import (
    get_pyproject_version,
    sync_pyproject_version,
)
from version_sync.pyfile import (
    get_pyfile_version,
    sync_pyfile_version,
)

# ======= PACKAGE_JSON TESTS =======


def test_get_packagejson_version(tmp_path):
    # Create a temporary package.json with a version field
    package_json_content = {"name": "test-package", "version": "1.2.3"}
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text(json.dumps(package_json_content))

    version = get_packagejson_version(str(pkg_file))
    assert version == "1.2.3"


def test_sync_packagejson_version(tmp_path):
    package_json_content = {"name": "test-package", "version": "1.2.3"}
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text(json.dumps(package_json_content, indent=2))
    new_version = Version("2.0.0")
    sync_package_json_version(str(pkg_file), new_version)

    # Re-read the file and verify the version is updated
    updated_content = json.loads(pkg_file.read_text())
    assert updated_content["version"] == "2.0.0"


# ======= PYPROJECT_TOML TESTS =======


def test_get_pyproject_version_poetry(tmp_path):
    # Create a temporary pyproject.toml using the [tool.poetry] section
    pyproject_content = textwrap.dedent(
        """
        [tool.poetry]
        version = "1.2.3"
    """
    )
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(pyproject_content)

    version = get_pyproject_version(pyproject_file)
    assert version == "1.2.3"


def test_get_pyproject_version_project(tmp_path):
    # Create a temporary pyproject.toml using the [project] section
    pyproject_content = textwrap.dedent(
        """
        [project]
        version = "1.2.3"
    """
    )
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(pyproject_content)

    version = get_pyproject_version(pyproject_file)
    assert version == "1.2.3"


def test_sync_pyproject_version(tmp_path):
    # Create a pyproject.toml with a [tool.poetry] section
    pyproject_content = textwrap.dedent(
        """
        [tool.poetry]
        version = "1.2.3"
    """
    )
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text(pyproject_content)

    new_version = Version("2.0.0")
    sync_pyproject_version(pyproject_file, new_version)

    # Read and verify the updated version using toml package
    from toml import loads as toml_loads

    updated_data = toml_loads(pyproject_file.read_text())
    assert updated_data["tool"]["poetry"]["version"] == "2.0.0"


# ======= PYFILE TESTS =======


def test_get_pyfile_version(tmp_path):
    # Create a temporary Python file with a version assignment
    py_file_content = textwrap.dedent(
        """
        # This is a test file.
        __version__ = "1.2.3"
    """
    )
    py_file = tmp_path / "test.py"
    py_file.write_text(py_file_content)

    version = get_pyfile_version(str(py_file), ["__version__"])
    assert version == "1.2.3"


def test_sync_pyfile_version(tmp_path):
    # Create a temporary Python file with a version assignment
    py_file_content = textwrap.dedent(
        """
        # A sample python file
        __version__ = "1.2.3"
        def foo():
            return 42
    """
    )
    py_file = tmp_path / "test.py"
    py_file.write_text(py_file_content)

    new_version = "2.0.0"
    sync_pyfile_version(py_file, ["__version__"], new_version)

    # Verify that the version string is updated in the file
    updated_content = py_file.read_text()
    match = re.search(r'__version__\s*=\s*[\'"](.*?)[\'"]', updated_content)
    assert match is not None
    assert match.group(1) == new_version


# ======= ERROR HANDLING TESTS =======


def test_get_packagejson_version_file_not_found(tmp_path):
    # Test for non-existing file should exit with SystemExit
    non_existent_file = tmp_path / "nonexistent.json"
    with pytest.raises(SystemExit):
        get_packagejson_version(str(non_existent_file))


def test_get_pyproject_version_file_not_found(tmp_path):
    non_existent_file = tmp_path / "nonexistent.toml"
    with pytest.raises(SystemExit):
        get_pyproject_version(non_existent_file)


def test_get_pyfile_version_file_not_found(tmp_path):
    non_existent_file = tmp_path / "nonexistent.py"
    with pytest.raises(SystemExit):
        get_pyfile_version(str(non_existent_file), ["__version__"])


# ======= MAIN INTEGRATION TESTS =======
# These tests simulate a full run using the main() function.
# We use monkeypatch to set sys.argv and capsys to capture output.

from version_sync.__main__ import main


def test_main_consistency(tmp_path, monkeypatch, capsys):
    # Create temporary files for pyproject.toml, package.json, and a Python file with version
    pyproject_content = textwrap.dedent(
        """
        [project]
        version = "1.2.3"
    """
    )
    pkg_content = json.dumps({"version": "1.2.3"}, indent=2)
    py_file_content = textwrap.dedent(
        """
        __version__ = "1.2.3"
    """
    )

    pyproject_file = tmp_path / "pyproject.toml"
    pkg_file = tmp_path / "package.json"
    py_file = tmp_path / "test.py"

    pyproject_file.write_text(pyproject_content)
    pkg_file.write_text(pkg_content)
    py_file.write_text(py_file_content)

    # Build fake command line arguments
    args = [
        "--py-vars",
        "__version__",
        str(py_file),
        str(pyproject_file),
        str(pkg_file),
    ]
    monkeypatch.setattr("sys.argv", ["version_sync"] + args)

    with pytest.raises(SystemExit) as e:
        main()
    # Expect exit code 0 because versions match
    assert e.value.code == 0
    captured = capsys.readouterr().out
    assert "Versions match" in captured


def test_main_sync(tmp_path, monkeypatch, capsys):
    # Create temporary files with different versions.
    # The highest among "1.0.0", "1.2.3", "1.1.0" is 1.2.3.
    pyproject_content = textwrap.dedent(
        """
        [project]
        version = "1.0.0"
    """
    )
    pkg_content = json.dumps({"version": "1.2.3"}, indent=2)
    py_file_content = textwrap.dedent(
        """
        __version__ = "1.1.0"
    """
    )

    pyproject_file = tmp_path / "pyproject.toml"
    pkg_file = tmp_path / "package.json"
    py_file = tmp_path / "test.py"

    pyproject_file.write_text(pyproject_content)
    pkg_file.write_text(pkg_content)
    py_file.write_text(py_file_content)

    # Include the --sync flag so that all files should be updated to "1.2.3"
    args = [
        "--py-vars",
        "__version__",
        "--sync",
        str(py_file),
        str(pyproject_file),
        str(pkg_file),
    ]
    monkeypatch.setattr("sys.argv", ["version_sync"] + args)

    with pytest.raises(SystemExit) as e:
        main()
    # Expect exit code 0 after successful sync
    assert e.value.code == 0

    # Re-read and verify that all files have the highest version "1.2.3"
    # Test pyproject.toml
    from toml import loads as toml_loads

    updated_pyproject = toml_loads(pyproject_file.read_text())
    assert updated_pyproject["project"]["version"] == "1.2.3"

    # Test package.json
    updated_pkg = json.loads(pkg_file.read_text())
    assert updated_pkg["version"] == "1.2.3"

    # Test Python file
    updated_py_file = py_file.read_text()
    match = re.search(r'__version__\s*=\s*[\'"](.*?)[\'"]', updated_py_file)
    assert match is not None
    assert match.group(1) == "1.2.3"

    captured = capsys.readouterr().out
    assert "Synchronization complete" in captured
