# :coding: utf-8

import os

import pytest
import wiz

import qip.definition


@pytest.fixture()
def mocked_wiz_load_definition(mocker):
    """Return mocked 'wiz.load_definition' function"""
    return mocker.patch.object(wiz, "load_definition")


def test_create(logger):
    """Create a definition from package mapping."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
    }

    result = qip.definition.create(mapping, "/path/to/installed/package")
    assert result == {
        "identifier": "foo",
        "version": "0.2.3",
        "install-location": "/path/to/installed/package",
        "group": "python"
    }

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_description(logger):
    """Create a definition from package mapping with description."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a package"
    }

    result = qip.definition.create(mapping, "/path/to/installed/package")
    assert result == {
        "identifier": "foo",
        "version": "0.2.3",
        "description": "This is a package",
        "install-location": "/path/to/installed/package",
        "group": "python"
    }

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_system(logger):
    """Create a definition from package mapping with system."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": {
                "name": "centos",
                "major_version": 7
            }
        }
    }

    result = qip.definition.create(mapping, "/path/to/installed/package")
    assert result == {
        "identifier": "foo",
        "version": "0.2.3",
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": "centos >= 7, < 8"
        },
        "install-location": "/path/to/installed/package",
        "group": "python"
    }

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_requirements(logger):
    """Create a definition from package mapping with requirements."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "requirements": [
            {
                "identifier": "?",
                "request": "bim >= 3, < 4",
            },
            {
                "identifier": "?",
                "request": "bar",
            }
        ]
    }

    result = qip.definition.create(mapping, "/path/to/installed/package")
    assert result == {
        "identifier": "foo",
        "version": "0.2.3",
        "install-location": "/path/to/installed/package",
        "group": "python",
        "requirements": [
            "bim >= 3, < 4",
            "bar"
        ]
    }

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_existing_lib(temporary_directory, logger):
    """Create a definition from package mapping."""
    os.makedirs(
        os.path.join(
            temporary_directory, "Foo", "Foo-0.2.3", "lib", "python2.7",
            "site-packages"
        )
    )

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3"
    }

    result = qip.definition.create(mapping, temporary_directory)
    assert result == {
        "identifier": "foo",
        "version": "0.2.3",
        "install-location": temporary_directory,
        "group": "python",
        "environ": {
            "PYTHONPATH": (
                "${INSTALL_LOCATION}/Foo/Foo-0.2.3/lib/python2.7/site-packages:"
                "${PYTHONPATH}"
            )
        }
    }

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_existing_bin(temporary_directory, logger):
    """Create a definition from package mapping."""
    os.makedirs(os.path.join(temporary_directory, "Foo", "Foo-0.2.3", "bin"))

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3"
    }

    result = qip.definition.create(mapping, temporary_directory)
    assert result == {
        "identifier": "foo",
        "version": "0.2.3",
        "install-location": temporary_directory,
        "group": "python",
        "environ": {
            "PATH": "${INSTALL_LOCATION}/Foo/Foo-0.2.3/bin:${PATH}"
        }
    }

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_retrieve_non_existing(mocked_wiz_load_definition, logger):
    """Fail to retrieve non existing definition from package mapping."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo"
    }

    result = qip.definition.retrieve(mapping, "/path/to/installed/package")
    assert result is None

    mocked_wiz_load_definition.assert_not_called()
    logger.info.assert_not_called()


def test_retrieve(temporary_directory, mocked_wiz_load_definition, logger):
    """Retrieve existing definition from package mapping."""
    path = os.path.join(temporary_directory, "share", "wiz", "Foo")
    os.makedirs(path)
    with open(os.path.join(path, "wiz.json"), "w") as stream:
        stream.write("")

    mocked_wiz_load_definition.return_value = "__DEFINITION__"

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo"
    }

    result = qip.definition.retrieve(mapping, temporary_directory)
    assert result == "__DEFINITION__"

    mocked_wiz_load_definition.assert_called_once_with(
        os.path.join(path, "wiz.json")
    )
    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )


@pytest.mark.parametrize("definition, expected", [
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "install-location": "/tmp/output"
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}/lib/python2.7/site-packages:${PYTHONPATH}",
                "TEST": "True"
            }
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}/foo/foo-0.1.0/lib/python2.7/site-packages:${PYTHONPATH}",
                "TEST": "True"
            },
            "install-location": "/tmp/output"
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "system": {
                "os": "el >= 7, < 8",
                "arch": "x86_64"
            },
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}/lib/python2.7/site-packages:${PYTHONPATH}",
                "TEST": "True"
            }
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "system": {
                "os": "el >= 7, < 8",
                "arch": "x86_64"
            },
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}/foo/foo-0.1.0/lib/python2.7/site-packages:${PYTHONPATH}",
                "TEST": "True"
            },
            "install-location": "/tmp/output"
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "variants": [
                {
                    "identifier": "variant1",
                    "environ": {
                        "PATH": "${INSTALL_LOCATION}/bin:${PATH}"
                    }
                }
            ]
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "variants": [
                {
                    "identifier": "variant1",
                    "environ": {
                        "PATH": "${INSTALL_LOCATION}/foo/foo-0.1.0/bin:${PATH}"
                    }
                }
            ],
            "install-location": "/tmp/output"
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}/lib/python2.7/site-packages:${PYTHONPATH}"
            },
            "variants": [
                {
                    "identifier": "variant1",
                    "environ": {
                        "PATH": "${INSTALL_LOCATION}/bin:${PATH}"
                    }
                }
            ]
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}/foo/foo-0.1.0/lib/python2.7/site-packages:${PYTHONPATH}"
            },
            "variants": [
                {
                    "identifier": "variant1",
                    "environ": {
                        "PATH": "${INSTALL_LOCATION}/foo/foo-0.1.0/bin:${PATH}"
                    }
                }
            ],
            "install-location": "/tmp/output"
        }
    )
], ids=[
    "no environ",
    "only environ",
    "with system",
    "with variants",
    "with environ and variants"
])
def test_update_install_location(definition, expected):
    _definition = wiz.definition.Definition(definition)
    _expected = wiz.definition.Definition(expected)

    result = qip.definition._update_install_location(
        _definition, "/tmp/output", "foo/foo-0.1.0"
    )

    assert result == _expected
