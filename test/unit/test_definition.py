# :coding: utf-8

import os

import pytest
import wiz
import wiz.exception
import wiz.definition

import qip.definition


@pytest.fixture()
def mocked_wiz_export_definition(mocker):
    """Return mocked 'wiz.export_definition' function"""
    return mocker.patch.object(wiz, "export_definition")


@pytest.fixture()
def mocked_wiz_load_definition(mocker):
    """Return mocked 'wiz.load_definition' function"""
    return mocker.patch.object(wiz, "load_definition")


@pytest.fixture()
def mocked_wiz_fetch_definition(mocker):
    """Return mocked 'wiz.fetch_definition' function"""
    return mocker.patch.object(wiz, "fetch_definition")


@pytest.fixture()
def mocked_retrieve(mocker):
    """Return mocked 'qip.definition.retrieve' function"""
    return mocker.patch.object(qip.definition, "retrieve")


@pytest.fixture()
def mocked_update(mocker):
    """Return mocked 'qip.definition.update' function"""
    return mocker.patch.object(qip.definition, "update")


@pytest.fixture()
def mocked_create(mocker):
    """Return mocked 'qip.definition.create' function"""
    return mocker.patch.object(qip.definition, "create")


def test_export(
    mocked_retrieve, mocked_update, mocked_create,
    mocked_wiz_fetch_definition, mocked_wiz_export_definition
):
    """Export definition."""
    mocked_retrieve.return_value = None
    mocked_create.return_value = "__DEF__"

    mapping = {"request": "foo >= 1, < 2"}
    path = "/definitions"
    package_path = "/path/lib/site-packages"
    output_path = "/packages"

    qip.definition.export(path, mapping, package_path, output_path)

    mocked_wiz_fetch_definition.assert_not_called()
    mocked_retrieve.assert_called_once_with(package_path, mapping)
    mocked_update.assert_not_called()
    mocked_create.assert_called_once_with(
        mapping, output_path, editable_mode=False,
        additional_variants=None
    )
    mocked_wiz_export_definition.assert_called_once_with(
        path, "__DEF__", overwrite=True
    )


def test_export_with_additional_variants(
    mocker, mocked_retrieve, mocked_update, mocked_create,
    mocked_wiz_fetch_definition, mocked_wiz_export_definition
):
    """Export definition with additional variants."""
    mocked_retrieve.return_value = None
    mocked_create.return_value = "__DEF__"
    mocked_wiz_fetch_definition.return_value = mocker.Mock(
        variants="__VARIANTS__"
    )

    mapping = {"request": "foo >= 1, < 2"}
    path = "/definitions"
    package_path = "/path/lib/site-packages"
    output_path = "/packages"

    qip.definition.export(
        path, mapping, package_path, output_path,
        definition_mapping="__MAPPING__"
    )

    mocked_wiz_fetch_definition.assert_called_once_with(
        "library::foo >= 1, < 2", "__MAPPING__"
    )
    mocked_retrieve.assert_called_once_with(package_path, mapping)
    mocked_update.assert_not_called()
    mocked_create.assert_called_once_with(
        mapping, output_path, editable_mode=False,
        additional_variants="__VARIANTS__"
    )
    mocked_wiz_export_definition.assert_called_once_with(
        path, "__DEF__", overwrite=True
    )


def test_export_with_request_error(
    mocked_retrieve, mocked_update, mocked_create,
    mocked_wiz_fetch_definition, mocked_wiz_export_definition
):
    """Impossible to find definition request in definition mapping."""
    mocked_retrieve.return_value = None
    mocked_create.return_value = "__DEF__"
    mocked_wiz_fetch_definition.side_effect = wiz.exception.RequestNotFound

    mapping = {"request": "foo >= 1, < 2"}
    path = "/definitions"
    package_path = "/path/lib/site-packages"
    output_path = "/packages"

    qip.definition.export(
        path, mapping, package_path, output_path,
        definition_mapping="__MAPPING__"
    )

    mocked_wiz_fetch_definition.assert_called_once_with(
        "library::foo >= 1, < 2", "__MAPPING__"
    )
    mocked_retrieve.assert_called_once_with(package_path, mapping)
    mocked_update.assert_not_called()
    mocked_create.assert_called_once_with(
        mapping, output_path, editable_mode=False,
        additional_variants=None
    )
    mocked_wiz_export_definition.assert_called_once_with(
        path, "__DEF__", overwrite=True
    )


def test_export_retrieved(
    mocker, mocked_retrieve, mocked_update, mocked_create,
    mocked_wiz_fetch_definition, mocked_wiz_export_definition
):
    """Export definition with previous one retrieved."""
    definition = mocker.Mock(namespace="plugin")

    mocked_retrieve.return_value = definition
    mocked_update.return_value = "__DEF__"

    mapping = {"request": "foo >= 1, < 2"}
    path = "/definitions"
    package_path = "/path/lib/site-packages"
    output_path = "/packages"

    qip.definition.export(path, mapping, package_path, output_path)

    mocked_wiz_fetch_definition.assert_not_called()
    mocked_retrieve.assert_called_once_with(package_path, mapping)
    mocked_update.assert_called_once_with(
        definition, mapping, output_path, editable_mode=False,
        additional_variants=None
    )
    mocked_create.assert_not_called()
    mocked_wiz_export_definition.assert_called_once_with(
        path, "__DEF__", overwrite=True
    )


def test_export_retrieved_and_additional_variants(
    mocker, mocked_retrieve, mocked_update, mocked_create,
    mocked_wiz_fetch_definition, mocked_wiz_export_definition
):
    """Export definition with previous one retrieved and additional variants."""
    definition = mocker.Mock(namespace="plugin")

    mocked_retrieve.return_value = definition
    mocked_update.return_value = "__DEF__"
    mocked_wiz_fetch_definition.return_value = mocker.Mock(
        variants="__VARIANTS__"
    )

    mapping = {"request": "foo >= 1, < 2"}
    path = "/definitions"
    package_path = "/path/lib/site-packages"
    output_path = "/packages"

    qip.definition.export(
        path, mapping, package_path, output_path,
        definition_mapping="__MAPPING__"
    )

    mocked_wiz_fetch_definition.assert_called_once_with(
        "plugin::foo >= 1, < 2", "__MAPPING__"
    )
    mocked_retrieve.assert_called_once_with(package_path, mapping)
    mocked_update.assert_called_once_with(
        definition, mapping, output_path, editable_mode=False,
        additional_variants="__VARIANTS__"
    )
    mocked_create.assert_not_called()
    mocked_wiz_export_definition.assert_called_once_with(
        path, "__DEF__", overwrite=True
    )


def test_retrieve_non_existing(mocked_wiz_load_definition, logger):
    """Fail to update non existing definition from package mapping."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "target": "Foo/Foo-0.2.3"
    }

    result = qip.definition.retrieve("/tmp_path", mapping)
    assert result is None

    mocked_wiz_load_definition.assert_not_called()
    logger.info.assert_not_called()


def test_retrieve(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed."""
    path = os.path.join(temporary_directory, "share", "wiz", "Foo", "wiz.json")
    _ensure_exists(path)

    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mocked_wiz_load_definition.return_value = definition

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
    }

    _definition = qip.definition.retrieve(temporary_directory, mapping)

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


def test_retrieve_from_source_location(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Retrieve definition from package installed with source location."""
    path = os.path.join(temporary_directory, "foo", "wiz.json")
    _ensure_exists(path)

    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library"
    })

    mocked_wiz_load_definition.return_value = definition

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
        "location": os.path.join(temporary_directory, "foo", "source"),
    }

    _definition = qip.definition.retrieve(temporary_directory, mapping)

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    logger.info.assert_called_once_with(
        "Wiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_any_call(path)


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
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
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
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
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
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
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
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
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
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
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
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9",
                    "bim[2.8] >= 3, < 4",
                    "bar[2.8]",
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
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
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
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
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
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": "/path/to/source",
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_additional_variants_1(logger):
    """Create a definition from package mapping with additional variants."""
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
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        }
    }

    result = qip.definition.create(
        mapping, "/path/to/installed/package",
        editable_mode=False,
        additional_variants=[
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "variant",
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "2.8",
                "environ": {"KEY28": "VALUE28"},
                "requirements": [
                    "bim[2.8] >= 3, < 4",
                    "baz"
                ]
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            })
        ]
    )
    assert result == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "namespace": "library",
        "description": "This is a package",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}",
        },
        "variants": [
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "environ": {
                    "KEY28": "VALUE28"
                },
                "requirements": [
                    "bim[2.8] >= 3, < 4",
                    "baz",
                    "python >=2.8, <2.9",
                    "bar[2.8]",
                ]
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            },
            {
                "identifier": "variant",
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_create_with_additional_variants_2(logger):
    """Create a definition from package mapping with additional variants."""
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
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        }
    }

    result = qip.definition.create(
        mapping, "/path/to/installed/package",
        editable_mode=False,
        additional_variants=[
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "variant",
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            })
        ]
    )
    assert result == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/path/to/installed/package",
        "namespace": "library",
        "description": "This is a package",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}",
        },
        "variants": [
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9",
                    "bim[2.8] >= 3, < 4",
                    "bar[2.8]",
                ]
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            },
            {
                "identifier": "variant",
            }
        ]
    })

    logger.info.assert_called_once_with(
        "Wiz definition created for 'Foo-0.2.3'."
    )


def test_update():
    """Update definition with mapping."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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


def test_update_with_pythonpath():
    """Update definition with mapping."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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


def test_update_without_description():
    """Update definition without description."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a cool library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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


def test_update_without_version():
    """Update definition without version."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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


def test_update_without_namespace():
    """Update definition without namespace."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "description": "This is a library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "library",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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


def test_update_with_system():
    """Update definition with system."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "key": "foo",
        "version": "0.2.3",
        "description": "This is a cool library",
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": {
                "name": "centos",
                "major_version": 7
            }
        }
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
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
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })


def test_update_with_commands():
    """Update definition with commands."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
        "command": {
            "foo": "python -m foo"
        }
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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


def test_update_with_commands_updated():
    """Update definition with commands updated."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "command": {
            "test": "Test",
            "foo": "FooX"
        }
    })

    mapping = {
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
        "command": {
            "foo": "python -m foo"
        }
    }

    _definition = qip.definition.update(definition, mapping, "/packages")

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "install-root": "/packages",
        "namespace": "plugin",
        "description": "This is a library",
        "command": {
            "test": "Test",
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
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


def test_update_editable():
    """Update definition with mapping in editable mode."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "target": "Foo/Foo-0.2.3",
        "location": "/path/to/lib",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(
        definition, mapping, "/packages", editable_mode=True
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": "/path/to/lib",
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            }
        ]
    })


def test_update_with_additional_variants_1():
    """Update definition with mapping with additional variants."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(
        definition, mapping, "/packages",
        additional_variants=[
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "variant",
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "2.8",
                "environ": {"KEY28": "VALUE28"}
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            })
        ]
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}",
        },
        "variants": [
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "environ": {
                    "KEY28": "VALUE28"
                },
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            },
            {
                "identifier": "variant",
            }
        ]
    })


def test_update_with_additional_variants_2():
    """Update definition with mapping with additional variants."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    mapping = {
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    _definition = qip.definition.update(
        definition, mapping, "/packages",
        additional_variants=[
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "variant",
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            }),
            wiz.definition._Variant({
                "definition": "__DEF__",
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            })
        ]
    )

    assert _definition == wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >=2.8, <2.9"
                ]
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            },
            {
                "identifier": "variant",
            }
        ]
    })


def _ensure_exists(path):
    """Ensure that *path* file exists."""
    os.makedirs(os.path.dirname(path))
    with open(path, "w") as stream:
        stream.write("")
