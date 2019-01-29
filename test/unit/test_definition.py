# :coding: utf-8

import os

import pytest
import wiz

import qip.definition


@pytest.fixture()
def mocked_wiz_load_definition(mocker):
    """Return mocked 'wiz.load_definition' function"""
    return mocker.patch.object(wiz, "load_definition")


@pytest.fixture()
def mocked_update_install_location(mocker):
    """Return mocked '_update_install_location' function"""
    return mocker.patch.object(qip.definition, "_update_install_location")


def test_create(logger):
    """Create a definition from package mapping."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package"
    }

    result = qip.definition.create(mapping, "/path/to/installed/package", False)
    assert sorted(result.to_dict()) == sorted({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "install-location": (
            "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.7/site-packages"
        ),
        "namespace": "library",
        "description": "This is a package"
    })

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
        },
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package"
    }

    result = qip.definition.create(mapping, "/path/to/installed/package", False)
    assert sorted(result.to_dict()) == sorted({
        "identifier": "foo",
        "version": "0.2.3",
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": "centos >= 7, < 8"
        },
        "install-root": "/path/to/installed/package",
        "install-location": (
            "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.7/site-packages"
        ),
        "namespace": "library",
        "description": "This is a package"
    })

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
            "bim >= 3, < 4",
            "bar",
        ],
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package"
    }

    result = qip.definition.create(mapping, "/path/to/installed/package", False)
    assert sorted(result.to_dict()) == sorted({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "install-location": (
            "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.7/site-packages"
        ),
        "namespace": "library",
        "requirements": [
            "bim >= 3, < 4",
            "bar"
        ],
        "description": "This is a package"
    })

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
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package"
    }

    result = qip.definition.create(mapping, temporary_directory, False)
    assert sorted(result.to_dict()) == sorted({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": temporary_directory,
        "install-location": (
            "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.7/site-packages"
        ),
        "namespace": "library",
        "environ": {
            "PYTHONPATH": (
                "${INSTALL_LOCATION}/Foo/Foo-0.2.3/lib/python2.7/site-packages:"
                "${PYTHONPATH}"
            )
        },
        "description": "This is a package"
    })

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_retrieve_non_existing(mocked_wiz_load_definition, logger):
    """Fail to retrieve non existing definition from package mapping."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "target": "Foo/Foo-0.2.3"
    }

    result = qip.definition.retrieve(mapping, "/tmp_path", "output_path", False)
    assert result is None

    mocked_wiz_load_definition.assert_not_called()
    logger.info.assert_not_called()


@pytest.mark.parametrize("definition, expected", [
    (
        {
            "identifier": "foo",
            "version": "0.1.0"
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            )
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}",
                "TEST": "True"
            }
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            ),
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}",
                "TEST": "True"
            }
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
                "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
            }
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "system": {
                "os": "el >= 7, < 8",
                "arch": "x86_64"
            },
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            ),
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
            }
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            ),
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
            },
            "variants": [
                {
                    "identifier": "variant1",
                    "environ": {
                        "PATH": "${INSTALL_LOCATION}/bin:${PATH}"
                    }
                }
            ]
        }
    )
], ids=[
    "no-environ",
    "environ",
    "system",
    "variants",
])
def test_retrieve(
    mocked_wiz_load_definition, temporary_directory, definition, expected,
    logger
):
    """Retrieve existing definition from package mapping and update."""
    _definition = wiz.definition.Definition(definition)
    _expected = wiz.definition.Definition(expected)

    path = os.path.join(temporary_directory, "share", "wiz", "Foo")
    os.makedirs(path)
    with open(os.path.join(path, "wiz.json"), "w") as stream:
        stream.write("")

    mocked_wiz_load_definition.return_value = _definition

    mapping = {
        "identifier": "Foo-0.1.0",
        "name": "Foo",
        "target": "Foo/Foo-0.1.0",
        "version": "0.1.0",
        "description": "This is a package"
    }

    result = qip.definition.retrieve(
        mapping, temporary_directory, "/path/to/installed/package", False
    )

    assert result == _expected

    mocked_wiz_load_definition.assert_called_once_with(
        os.path.join(path, "wiz.json")
    )
    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.1.0'."
    )


@pytest.mark.parametrize("definition, editable, expected", [
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
        },
        False,
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            )
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
        },
        True,
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "install-location": "/source"
        }
    )
], ids=[
    "not editable",
    "editable"
])
def test_update_install_location(definition, editable, expected):
    """Update install location and root."""
    _definition = wiz.definition.Definition(definition)
    _expected = wiz.definition.Definition(expected)

    mapping = {
        "identifier": "Foo-0.1.0",
        "name": "Foo",
        "target": "Foo/Foo-0.1.0",
        "location": "/source",
        "version": "0.1.0",
        "description": "This is a package"
    }

    result = qip.definition.update_definition(
        _definition, mapping, "/path/to/installed/package",
        editable_mode=editable
    )

    assert result == _expected


@pytest.mark.parametrize("definition, mapping, expected", [
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
        },
        {
            "command": {"foo": "foo"},
            "target": "Foo/Foo-0.1.0",
            "version": "0.1.0",
            "description": "This is a package"
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "command": {"foo": "foo"},
            "install-root": "/path/to/installed/package",
            "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            )
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "command": {"bar": "bar"}
        },
        {
            "command": {"foo": "foo"},
            "target": "Foo/Foo-0.1.0",
            "version": "0.1.0",
            "description": "This is a package"
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "command": {"bar": "bar", "foo": "foo"},
            "install-root": "/path/to/installed/package",
            "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            )
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
        },
        {
            "target": "Foo/Foo-0.1.0",
            "version": "0.1.0",
            "description": "This is a package"
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            )
        }
    )
], ids=[
    "without existing commands",
    "with existing commands",
    "no mapping"
])
def test_update_command(definition, mapping, expected):
    """Update command."""
    _definition = wiz.definition.Definition(definition)
    _expected = wiz.definition.Definition(expected)

    result = qip.definition.update_definition(
        _definition, mapping, "/path/to/installed/package"
    )

    assert result == _expected


@pytest.mark.parametrize("definition, mapping, expected", [
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
        },
        {
            "target": "Foo/Foo-0.1.0",
            "requirements": ["mlog"],
            "version": "0.1.0",
            "description": "This is a package"
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            ),
            "requirements": ["mlog"]
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "requirements": ["maya"]
        },
        {
            "target": "Foo/Foo-0.1.0",
            "requirements": ["mlog"],
            "version": "0.1.0",
            "description": "This is a package"
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            ),
            "requirements": ["maya", "mlog"]
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
        },
        {
            "target": "Foo/Foo-0.1.0",
            "version": "0.1.0",
            "description": "This is a package"
        },
        {
            "identifier": "foo",

            "version": "0.1.0",
            "description": "This is a package",
            "install-root": "/path/to/installed/package",
            "install-location": (
                "${INSTALL_ROOT}/Foo/Foo-0.1.0/lib/python2.7/site-packages"
            )
        }
    )
], ids=[
    "without existing requirements",
    "with existing requirements",
    "no mapping"
])
def test_update_requirements(definition, mapping, expected):
    """Update requirements."""
    _definition = wiz.definition.Definition(definition)
    _expected = wiz.definition.Definition(expected)

    result = qip.definition.update_definition(
        _definition, mapping, "/path/to/installed/package",
    )

    assert result == _expected
