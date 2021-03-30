# :coding: utf-8

import sys
import os
import re
import importlib

import pytest
from six.moves import reload_module
from click.testing import CliRunner
import wiz
import wiz.config

import qip.command_line


#: Record name of python library path for convenience.
PY_LIB = "python{}.{}".format(sys.version_info.major, sys.version_info.minor)


@pytest.fixture(autouse=True)
def reset_configuration(mocker):
    """Ensure that no personal configuration is fetched during tests."""
    function = os.path.expanduser
    mocker.patch.object(os.path, "expanduser", return_value="__HOME__")

    # Reset configuration.
    qip.command_line._CONFIG = wiz.config.fetch(refresh=True)
    reload_module(qip.command_line)

    # Reset mock for 'os.path.expanduser' to prevent messing with the tests.
    mocker.patch.object(os.path, "expanduser", function)


def test_install_numpy(temporary_directory, logger):
    """Install numpy.

    Install numpy version within 1.16.6 and 1.20.2 which covers all Python
    version supported by Qip. numpy doesn't have any dependencies.

    """
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install",
            "numpy >= 1.16.6, <= 1.20.2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_called()
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check definitions installed.
    definitions = os.listdir(definitions_path)
    assert len(definitions) == 1
    assert re.match(r"^library-numpy-1..*.json$", definitions[0])
    path = os.path.join(definitions_path, definitions[0])
    assert os.path.isfile(path)

    # Ensure that definition is correct.
    definition = wiz.load_definition(path)
    assert definition.qualified_identifier == "library::numpy"
    assert definition.install_root == packages_path
    assert definition.system is not None
    assert definition.requirements == []
    assert definition.environ == {
        "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
    }
    assert len(definition.variants) == 1
    assert len(definition.variants[0].requirements) == 1
    assert definition.variants[0].requirements[0].name == "python"

    # Check package installed.
    assert len(os.listdir(packages_path)) == 1
    path = os.path.join(packages_path, "numpy")
    assert os.path.isdir(path)

    versions = os.listdir(path)
    assert len(versions) == 1
    assert re.match(r"^numpy-1..*", versions[0])
    lib_path = os.path.join(path, versions[0], "lib", PY_LIB, "site-packages")
    module_path = os.path.join(lib_path, "numpy")
    assert os.path.isdir(lib_path)
    assert os.path.isdir(module_path)

    # Check that module can be imported.
    sys.path.insert(0, lib_path)
    importlib.import_module("numpy")
    del sys.path[0]


def test_install_numpy_several_versions(temporary_directory, logger):
    """Install numpy.

    Like the previous test, install numpy version within 1.16.6 and 1.20.2 which
    covers all Python version supported by Qip. Then install numpy while
    excluding the latest versions supported by 2.7 and 3+ to force another
    version to get installed.

    """
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install",
            "numpy >= 1.16.6, <= 1.20.2",
            "numpy != 1.16.6, < 1.20.2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_called()
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check definitions installed.
    definitions = os.listdir(definitions_path)
    assert len(definitions) == 2
    assert definitions[0] != definitions[1]

    assert re.match(r"^library-numpy-1..*.json$", definitions[0])
    path = os.path.join(definitions_path, definitions[0])
    assert os.path.isfile(path)
    definition1 = wiz.load_definition(path)

    assert re.match(r"^library-numpy-1..*.json$", definitions[1])
    path = os.path.join(definitions_path, definitions[1])
    assert os.path.isfile(path)
    definition2 = wiz.load_definition(path)

    # Ensure that definitions are correct.
    for definition in [definition1, definition2]:
        assert definition.qualified_identifier == "library::numpy"
        assert definition.install_root == packages_path
        assert definition.system is not None
        assert definition.requirements == []
        assert definition.environ == {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        }
        assert len(definition.variants) == 1
        assert len(definition.variants[0].requirements) == 1
        assert definition.variants[0].requirements[0].name == "python"

    assert definition1.version != definition2.version

    # Check packages installed.
    assert len(os.listdir(packages_path)) == 1
    path = os.path.join(packages_path, "numpy")
    assert os.path.isdir(path)

    versions = os.listdir(path)
    assert len(versions) == 2

    for version in versions:
        assert re.match(r"^numpy-1..*", version)
        lib_path = os.path.join(path, version, "lib", PY_LIB, "site-packages")
        module_path = os.path.join(lib_path, "numpy")
        assert os.path.isdir(lib_path)
        assert os.path.isdir(module_path)

        # Check that module can be imported.
        sys.path.insert(0, lib_path)
        importlib.import_module("numpy")
        del sys.path[0]
