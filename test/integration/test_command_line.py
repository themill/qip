# :coding: utf-8

import os

import pytest
from six.moves import reload_module
from click.testing import CliRunner
import wiz
import wiz.registry
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


@pytest.fixture()
def registry_path(mocker, temporary_directory):
    """Mock default registry path."""
    registry_path = os.path.join(temporary_directory, "registry")
    os.makedirs(registry_path)
    mocker.patch.object(
        wiz.registry, "get_defaults", return_value=[registry_path]
    )
    return registry_path


def test_install(temporary_directory, logger):
    """Install packages with all dependencies."""
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

    # Check log.
    logger.info.assert_any_call(
        "Packages installed: Bar-0.1.0, BIM-3.6.2, Foo-1.2.0"
    )
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
        os.path.join("Bar", "Bar-0.1.0-py27-centos7"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bar-0.1.0-M2Uq9Esezm-m00VeWkTzkQIu3T4.json",
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json",
    ]

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


def test_install_editable_mode(temporary_directory, logger):
    """Install packages in editable mode."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install", "-e",
            "foo >= 1, <= 2",
            "bar == 0.1.0",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_any_call(
        "Packages installed: Bar-0.1.0, BIM-3.6.2, Foo-1.2.0"
    )
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
        os.path.join("Bar", "Bar-0.1.0-py27-centos7"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bar-0.1.0-M2Uq9Esezm-m00VeWkTzkQIu3T4.json",
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json",
    ]

    definitions = os.listdir(definitions_path)
    assert sorted(definitions) == expected_definitions

    path = os.path.join(definitions_path, expected_definitions[0])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "bar",
        "version": "0.1.0",
        "description": "Bar Python Package.",
        "namespace": "library",
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
                "install-location": "/path/to/bar",
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
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": "/path/to/foo",
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::bim[2.7] >=3.4, <5"
                ]
            }
        ]
    }


def test_install_with_optional_dependencies(temporary_directory, logger):
    """Install packages with optional dependencies."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install",
            "bim[test1]",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_any_call(
        "Packages installed: Baz-4.5.2, BIM-test1-3.6.2"
    )
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-test1-3.6.2-py27"),
        os.path.join("Baz", "Baz-4.5.2-py27"),
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-baz-4.5.2.json",
        "library-bim-test1-3.6.2.json",
    ]

    definitions = os.listdir(definitions_path)
    assert sorted(definitions) == expected_definitions

    path = os.path.join(definitions_path, expected_definitions[0])
    definition = wiz.load_definition(path)
    assert definition.data() == {
        "identifier": "baz",
        "version": "4.5.2",
        "description": "Baz Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/Baz/Baz-4.5.2-py27/lib/python2.7/"
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
        "identifier": "bim-test1",
        "version": "3.6.2",
        "description": "Bim Python Package.",
        "namespace": "library",
        "install-root": packages_path,
        "command": {
            "bim1": "python -m bim"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": (
                    "${INSTALL_ROOT}/BIM/BIM-test1-3.6.2-py27/lib/python2.7/"
                    "site-packages"
                ),
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::baz[2.7]"
                ]
            }
        ]
    }


def test_install_no_dependencies(temporary_directory, logger):
    """Install packages without dependencies."""
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

    # Check log.
    logger.info.assert_any_call("Packages installed: Bar-0.1.0, Foo-1.2.0")
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("Bar", "Bar-0.1.0-py27-centos7"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bar-0.1.0-M2Uq9Esezm-m00VeWkTzkQIu3T4.json",
        "library-foo-1.2.0.json",
    ]

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


def test_install_update_from_output(temporary_directory, logger):
    """Update existing definition in output definition path with new variants.
    """
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Export definition to update.
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

    # Check log.
    logger.info.assert_any_call("Packages installed: BIM-3.6.2, Foo-1.2.0")
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json",
    ]

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


def test_install_update_from_registry(
    temporary_directory, registry_path, logger
):
    """Update existing definition in registry path with new variants."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Export definition to update.
    wiz.export_definition(registry_path, {
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

    # Check log.
    logger.info.assert_any_call("Packages installed: BIM-3.6.2, Foo-1.2.0")
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json",
    ]

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


def test_install_skip_existing_definition(
    temporary_directory, registry_path, logger
):
    """Skip existing definition in registry path."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Export definition to skip.
    wiz.export_definition(registry_path, {
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
    })

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install",
            "foo >= 1, <= 2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_any_call("Packages installed: BIM-3.6.2")
    logger.warning.assert_called_once_with(
        "Skip 'foo[2.7]==1.2.0' which already exists in Wiz registries."
    )
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bim-3.6.2.json",
    ]

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


def test_install_editable_mode_with_existing_definition(
    temporary_directory, registry_path, logger
):
    """Do not skip existing definition in registry path in editable mode."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Export definition to skip.
    wiz.export_definition(registry_path, {
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
    })

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install", "-e",
            "foo >= 1, <= 2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_any_call("Packages installed: BIM-3.6.2, Foo-1.2.0")
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json"
    ]

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
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.7",
                "install-location": "/path/to/foo",
                "requirements": [
                    "python >= 2.7, < 2.8",
                    "library::bim[2.7] >=3.4, <5"
                ]
            }
        ]
    }


def test_install_ignore_registries(temporary_directory, registry_path, logger):
    """Install packages while ignoring existing definition in registry."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Export definition to ignore.
    wiz.export_definition(registry_path, {
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
    })

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install", "-I",
            "foo >= 1, <= 2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_any_call("Packages installed: BIM-3.6.2, Foo-1.2.0")
    logger.warning.assert_not_called()
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json"
    ]

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


def test_install_skip_package_installed(temporary_directory, logger):
    """Skip existing package in output package."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Create package to skip.
    os.makedirs(os.path.join(packages_path, "Foo", "Foo-1.2.0-py27"))

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install", "-s",
            "foo >= 1, <= 2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_any_call("Packages installed: BIM-3.6.2")
    logger.warning.assert_called_once_with(
        "Skip 'Foo-1.2.0' which is already installed."
    )
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = ["library-bim-3.6.2.json"]

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


def test_install_overwrite_package_installed(temporary_directory, logger):
    """Overwrite existing package in output package."""
    packages_path = os.path.join(temporary_directory, "packages")
    definitions_path = os.path.join(temporary_directory, "definitions")

    # Create package to overwrite.
    os.makedirs(os.path.join(packages_path, "Foo", "Foo-1.2.0-py27"))

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.main, [
            "install", "-f",
            "foo >= 1, <= 2",
            "-o", packages_path,
            "-d", definitions_path,
        ]
    )
    assert not result.exception
    assert result.exit_code == 0

    # Check log.
    logger.info.assert_any_call("Packages installed: BIM-3.6.2, Foo-1.2.0")
    logger.warning.assert_called_once_with(
        "Overwrite 'Foo-1.2.0' which is already installed."
    )
    logger.error.assert_not_called()

    # Check package installed.
    expected_packages = [
        os.path.join("BIM", "BIM-3.6.2-py27"),
        os.path.join("Foo", "Foo-1.2.0-py27")
    ]

    for package in expected_packages:
        assert os.path.isdir(os.path.join(packages_path, package))

    # Check definitions installed.
    expected_definitions = [
        "library-bim-3.6.2.json",
        "library-foo-1.2.0.json",
    ]

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
