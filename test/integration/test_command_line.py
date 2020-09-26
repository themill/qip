# :coding: utf-8

import os

import pytest
from six.moves import reload_module
from click.testing import CliRunner
import wiz
import wiz.config
import wiz.definition

import qip.command_line
import qip.command


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


def test_install(temporary_directory, logger):
    """Install a package with all dependencies."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install",
            "foo >= 1, <= 2",
            "bar == 0.1.0",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    logger.info.assert_any_call(
        "Packages installed: Bar-0.1.0, BIM-3.6.2, Foo-1.2.0"
    )
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    expected_packages = ["BIM", "Bar", "Foo"]

    expected_definitions = [
        "library-bar-0.1.0-M2Uq9Esezm-m00VeWkTzkQIu3T4.json",
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json",
    ]

    # Check definitions installed.
    definitions = os.listdir(definitions_path)
    assert sorted(definitions) == expected_definitions

    path = os.path.join(definitions_path, expected_definitions[0])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "bar",
        "version": "0.1.0",
        "description": "Bar Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "system": {
            "platform": "linux",
            "os": "centos >= 7, < 8",
            "arch": "x86_64"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/Bar/Bar-0.1.0-py27-centos7/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::foo[2.7]"
                ]
            }
        ]
    }

    path = os.path.join(definitions_path, expected_definitions[1])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "bim",
        "version": "3.6.2",
        "description": "Bim Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/BIM/BIM-3.6.2-py27/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                ]
            }
        ]
    }

    path = os.path.join(definitions_path, expected_definitions[2])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "foo",
        "version": "1.2.0",
        "description": "Foo Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-1.2.0-py27/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::bim[2.7] >=3.4, <5"
                ]
            }
        ]
    }

    # Check package installed.
    packages = os.listdir(packages_path)
    assert sorted(packages) == expected_packages

    for package in packages:
        assert os.path.isdir(os.path.join(packages_path, package))


def test_install_no_dependencies(temporary_directory, logger):
    """Install a package without dependencies."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install", "-N",
            "foo >= 1, <= 2",
            "bar == 0.1.0",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    logger.info.assert_any_call(
        "Packages installed: Bar-0.1.0, Foo-1.2.0"
    )
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    expected_packages = ["Bar", "Foo"]

    expected_definitions = [
        "library-bar-0.1.0-M2Uq9Esezm-m00VeWkTzkQIu3T4.json",
        "library-foo-1.2.0.json",
    ]

    # Check definitions installed.
    definitions = os.listdir(definitions_path)
    assert sorted(definitions) == expected_definitions

    path = os.path.join(definitions_path, expected_definitions[0])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "bar",
        "version": "0.1.0",
        "description": "Bar Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "system": {
            "platform": "linux",
            "os": "centos >= 7, < 8",
            "arch": "x86_64"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/Bar/Bar-0.1.0-py27-centos7/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::foo[2.7]"
                ]
            }
        ]
    }

    path = os.path.join(definitions_path, expected_definitions[1])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "foo",
        "version": "1.2.0",
        "description": "Foo Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-1.2.0-py27/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::bim[2.7] >=3.4, <5"
                ]
            }
        ]
    }

    # Check package installed.
    packages = os.listdir(packages_path)
    assert sorted(packages) == expected_packages

    for package in packages:
        assert os.path.isdir(os.path.join(packages_path, package))


def test_install_update(temporary_directory, logger):
    """Update existing packages with new variants."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Export definition to update.s
    wiz.export_definition(definitions_path, {
        "identifier": "foo",
        "version": "1.2.0",
        "description": "Foo Python Package.",
        "namespace": "library",
        "install-root": "/path/to/foo",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "3.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-1.2.0-py38/lib/python3.8/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 3.8, < 3.9",
                ]
            }
        ]
    })

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install", "-u",
            "foo >= 1, <= 2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    logger.info.assert_any_call(
        "Packages installed: BIM-3.6.2, Foo-1.2.0"
    )
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    expected_packages = ["BIM", "Foo"]

    expected_definitions = [
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json",
    ]

    # Check definitions installed.
    definitions = os.listdir(definitions_path)
    assert sorted(definitions) == expected_definitions

    path = os.path.join(definitions_path, expected_definitions[0])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "bim",
        "version": "3.6.2",
        "description": "Bim Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/BIM/BIM-3.6.2-py27/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                ]
            }
        ]
    }

    path = os.path.join(definitions_path, expected_definitions[1])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "foo",
        "version": "1.2.0",
        "description": "Foo Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "3.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-1.2.0-py38/lib/python3.8/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 3.8, < 3.9",
                ]
            },
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-1.2.0-py27/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::bim[2.7] >=3.4, <5"
                ]
            }
        ]
    }

    # Check package installed.
    packages = os.listdir(packages_path)
    assert sorted(packages) == expected_packages

    for package in packages:
        assert os.path.isdir(os.path.join(packages_path, package))
