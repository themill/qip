# :coding: utf-8

import os

import pytest
import wiz
import wiz.definition

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
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        }
    }

    result = qip.definition.create(
        mapping, "/path/to/installed/package", editable_mode=False
    )
    assert result == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "namespace": "library",
        "description": "This is a package",
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements": [
                    "python >=2.8, <2.9",
                ]
            }
        ]
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
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        }
    }

    result = qip.definition.create(
        mapping, "/path/to/installed/package", editable_mode=False
    )
    assert result == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "namespace": "library",
        "description": "This is a package",
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": "centos >= 7, < 8"
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements": [
                    "python >=2.8, <2.9",
                ]
            }
        ]
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
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        }
    }

    result = qip.definition.create(
        mapping, "/path/to/installed/package", editable_mode=False
    )
    assert result == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "namespace": "library",
        "description": "This is a package",
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements": [
                    "python >=2.8, <2.9",
                    "bim >= 3, < 4",
                    "bar",
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_commands(logger):
    """Create a definition from package mapping with commands."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "command": {
            "foo": "python -m foo",
            "test": "python -m foo.test",
        },
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        }
    }

    result = qip.definition.create(
        mapping, "/path/to/installed/package", editable_mode=False
    )
    assert result == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "namespace": "library",
        "description": "This is a package",
        "command": {
            "foo": "python -m foo",
            "test": "python -m foo.test",
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_editable_mode(logger):
    """Create a definition from package mapping in editable mode."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        },
        "location": "/path/to/source"
    }

    result = qip.definition.create(
        mapping, "/path/to/installed/package", editable_mode=True
    )
    assert result == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "description": "This is a package",
        "variants": [
            {
                "identifier": "2.8",
                "install-location": "/path/to/source",
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
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


def test_retrieve(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed."""
    path = os.path.join(temporary_directory, "share", "wiz", "Foo", "wiz.json")
    _ensure_exists(path)

    mocked_wiz_load_definition.return_value = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        }
    }

    _definition = qip.definition.retrieve(
        mapping, temporary_directory, "/path/to/installed/package",
        editable_mode=False
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "install-root": "/path/to/installed/package",
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


def test_retrieve_from_source_location(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed from source location."""
    path = os.path.join(temporary_directory, "foo", "wiz.json")
    _ensure_exists(path)

    mocked_wiz_load_definition.return_value = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "location": os.path.join(temporary_directory, "foo", "source"),
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        }
    }

    _definition = qip.definition.retrieve(
        mapping, temporary_directory, "/path/to/installed/package",
        editable_mode=False
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "install-root": "/path/to/installed/package",
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


def test_retrieve_with_commands(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed with commands."""
    path = os.path.join(temporary_directory, "share", "wiz", "Foo", "wiz.json")
    _ensure_exists(path)

    mocked_wiz_load_definition.return_value = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        },
        "command": {
            "foo": "python -m foo",
            "test": "python -m foo.test",
        }
    }

    _definition = qip.definition.retrieve(
        mapping, temporary_directory, "/path/to/installed/package",
        editable_mode=False
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "install-root": "/path/to/installed/package",
        "command": {
            "foo": "python -m foo",
            "test": "python -m foo.test",
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


def test_retrieve_with_commands_updated(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed with updated commands."""
    path = os.path.join(temporary_directory, "share", "wiz", "Foo", "wiz.json")
    _ensure_exists(path)

    mocked_wiz_load_definition.return_value = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "command": {
            "test": "python -m foo.test",
        }
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        },
        "command": {
            "foo": "python -m foo",
        }
    }

    _definition = qip.definition.retrieve(
        mapping, temporary_directory, "/path/to/installed/package",
        editable_mode=False
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "install-root": "/path/to/installed/package",
        "command": {
            "foo": "python -m foo",
            "test": "python -m foo.test",
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


def test_retrieve_with_existing_variant_1(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed with existing variant."""
    path = os.path.join(temporary_directory, "share", "wiz", "Foo", "wiz.json")
    _ensure_exists(path)

    mocked_wiz_load_definition.return_value = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "variants": [
            {
                "identifier": "2.8",
                "environ": {
                    "KEY": "VALUE"
                },
                "requirements": [
                    "python >=2.8, <2.9",
                    "bar >=2, < 3"
                ]
            }
        ]
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        },
        "requirements": [
            "bim"
        ]
    }

    _definition = qip.definition.retrieve(
        mapping, temporary_directory, "/path/to/installed/package",
        editable_mode=False
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "install-root": "/path/to/installed/package",
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "environ": {
                    "KEY": "VALUE"
                },
                "requirements": [
                    "python >=2.8, <2.9",
                    "bar >=2, < 3",
                    "bim",
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


def test_retrieve_with_existing_variant_2(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed with existing variant."""
    path = os.path.join(temporary_directory, "share", "wiz", "Foo", "wiz.json")
    _ensure_exists(path)

    mocked_wiz_load_definition.return_value = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "variants": [
            {
                "identifier": "3.6",
                "environ": {
                    "KEY": "VALUE"
                },
                "requirements": [
                    "python >=3.6, <3.7",
                    "bar >=2, < 3"
                ]
            }
        ]
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "target": "Foo/Foo-0.2.3",
        "description": "This is a package",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9"
        },
        "requirements": [
            "bim"
        ]
    }

    _definition = qip.definition.retrieve(
        mapping, temporary_directory, "/path/to/installed/package",
        editable_mode=False
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "install-root": "/path/to/installed/package",
        "variants": [
            {
                "identifier": "3.6",
                "environ": {
                    "KEY": "VALUE"
                },
                "requirements": [
                    "python >=3.6, <3.7",
                    "bar >=2, < 3"
                ]
            },
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9",
                    "bim"
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


def _ensure_exists(path):
    """Ensure that *path* file exists."""
    os.makedirs(os.path.dirname(path))
    with open(path, "w") as stream:
        stream.write("")
