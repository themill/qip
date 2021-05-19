# :coding: utf-8

import os
import functools

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
    """Return mocked 'wiz.definition.load' function"""
    return mocker.patch.object(wiz.definition, "load")


@pytest.fixture()
def mocked_wiz_fetch_definition(mocker):
    """Return mocked 'wiz.fetch_definition' function"""
    return mocker.patch.object(wiz, "fetch_definition")


@pytest.fixture()
def mocked_update(mocker):
    """Return mocked 'qip.definition.update' function"""
    return mocker.patch.object(qip.definition, "update")


@pytest.fixture()
def mocked_create(mocker):
    """Return mocked 'qip.definition.create' function"""
    return mocker.patch.object(qip.definition, "create")


@pytest.mark.parametrize("options, additional_variants, editable_mode", [
    ({}, None, False),
    ({"editable_mode": True}, None, True),
    (
        {
            "existing_definition": wiz.definition.Definition({
                "identifier": "foo",
                "variants": [{"identifier": "V3", "environ": {"KEY": "VALUE"}}]
            })
        },
        [{"identifier": "V3", "environ": {"KEY": "VALUE"}}], False
    ),
], ids=[
    "simple",
    "with-editable-mode",
    "with-additional-variants",
])
def test_export(
    mocked_update, mocked_create, mocked_wiz_export_definition, options,
    additional_variants, editable_mode
):
    """Export definition."""
    mapping = {"request": "foo >= 1, < 2"}
    path = "/definitions"
    output_path = "/packages"

    qip.definition.export(path, mapping, output_path, **options)

    mocked_update.assert_not_called()
    mocked_create.assert_called_once_with(
        mapping, output_path, editable_mode=editable_mode,
        additional_variants=additional_variants
    )
    mocked_wiz_export_definition.assert_called_once_with(
        path, mocked_create.return_value, overwrite=True
    )


@pytest.mark.parametrize("options, additional_variants, editable_mode", [
    ({}, None, False),
    ({"editable_mode": True}, None, True),
    (
        {
            "existing_definition": wiz.definition.Definition({
                "identifier": "foo",
                "variants": [{"identifier": "V3", "environ": {"KEY": "VALUE"}}]
            })
        },
        [{"identifier": "V3", "environ": {"KEY": "VALUE"}}], False
    ),
], ids=[
    "simple",
    "with-editable-mode",
    "with-additional-variants",
])
def test_export_from_custom_definition(
    mocked_update, mocked_create, mocked_wiz_export_definition, options,
    additional_variants, editable_mode
):
    """Export definition from custom definition retrieved."""
    mapping = {"request": "foo >= 1, < 2"}
    path = "/definitions"
    output_path = "/packages"

    qip.definition.export(
        path, mapping, output_path,
        custom_definition="__CUSTOM_DEFINITION__",
        **options
    )

    mocked_update.assert_called_once_with(
        "__CUSTOM_DEFINITION__", mapping, output_path,
        editable_mode=editable_mode,
        additional_variants=additional_variants
    )
    mocked_create.assert_not_called()
    mocked_wiz_export_definition.assert_called_once_with(
        path, mocked_update.return_value, overwrite=True
    )


def test_fetch_custom(mocked_wiz_load_definition, temporary_directory, logger):
    """Fetch custom definition from package installed."""
    mapping = {
        "key": "foo",
        "version": "0.2.3",
        "identifier": "Foo-0.2.3",
        "module_name": "foo",
        "location": temporary_directory,
        "extra": []
    }

    path = os.path.join(temporary_directory, "foo", "package_data", "wiz.json")

    os.makedirs(os.path.dirname(path))
    with open(path, "w") as stream:
        stream.write("")

    mocked_wiz_load_definition.return_value = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    })

    _definition = qip.definition.fetch_custom(mapping)

    assert _definition.data() == {
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
    }

    logger.info.assert_called_once_with(
        "\tWiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_called_once_with(
        path, mapping={"identifier": "foo", "version": "0.2.3"}
    )


def test_fetch_custom_with_extra(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Fetch extra custom definitions from package installed."""
    mapping = {
        "key": "foo",
        "version": "0.2.3",
        "identifier": "Foo-0.2.3",
        "module_name": "foo",
        "location": temporary_directory,
        "extra": ["test1", "test2"]
    }

    os.makedirs(os.path.join(temporary_directory, "foo", "package_data"))
    paths = [
        os.path.join(temporary_directory, "foo", "package_data", name)
        for name in ["wiz.json", "wiz-test1.json"]
    ]

    for path in paths:
        with open(path, "w") as stream:
            stream.write("")

    mocked_wiz_load_definition.side_effect = [
        wiz.definition.Definition({
            "identifier": "foo",
            "version": "0.2.3",
            "namespace": "plugin",
            "description": "This is a library",
            "environ": {"KEY1": "VALUE1"}
        }),
        wiz.definition.Definition({
            "identifier": "foo",
            "version": "0.2.3",
            "environ": {"KEY2": "VALUE2"},
            "requirements": [
                "bar >= 1.2, < 2"
            ]
        }),
    ]

    _definition = qip.definition.fetch_custom(mapping)

    assert _definition.data() == {
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "environ": {
            "KEY1": "VALUE1",
            "KEY2": "VALUE2",
        },
        "requirements": [
            "bar >= 1.2, < 2"
        ]
    }

    logger.info.assert_called_once_with(
        "\tWiz definition extracted from 'Foo-0.2.3'."
    )

    assert mocked_wiz_load_definition.call_count == 2
    mocked_wiz_load_definition.assert_any_call(
        paths[0], mapping={"identifier": "foo", "version": "0.2.3"}
    )
    mocked_wiz_load_definition.assert_any_call(
        paths[1], mapping={"identifier": "foo", "version": "0.2.3"}
    )


def test_fetch_custom_with_extra_only(
    mocked_wiz_load_definition, temporary_directory, logger
):
    """Fetch only extra custom definition from package installed."""
    mapping = {
        "key": "foo",
        "version": "0.2.3",
        "identifier": "Foo-0.2.3",
        "module_name": "foo",
        "location": temporary_directory,
        "extra": ["test1", "test2"]
    }

    path = os.path.join(
        temporary_directory, "foo", "package_data", "wiz-test1.json"
    )

    os.makedirs(os.path.dirname(path))
    with open(path, "w") as stream:
        stream.write("")

    mocked_wiz_load_definition.side_effect = [
        wiz.definition.Definition({
            "identifier": "foo",
            "version": "0.2.3",
            "environ": {"KEY2": "VALUE2"},
            "requirements": [
                "bar >= 1.2, < 2"
            ]
        }),
    ]

    _definition = qip.definition.fetch_custom(mapping)

    assert _definition.data() == {
        "identifier": "foo",
        "version": "0.2.3",
        "environ": {
            "KEY2": "VALUE2",
        },
        "requirements": [
            "bar >= 1.2, < 2"
        ]
    }

    logger.info.assert_called_once_with(
        "\tWiz definition extracted from 'Foo-0.2.3'."
    )

    mocked_wiz_load_definition.assert_called_once_with(
        path, mapping={"identifier": "foo", "version": "0.2.3"}
    )


def test_fetch_custom_empty(mocked_wiz_load_definition, logger):
    """Fail to fetch custom definition from package mapping."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "module_name": "foo",
        "location": "/path/to/lib",
        "extra": []
    }

    result = qip.definition.fetch_custom(mapping)
    assert result is None

    mocked_wiz_load_definition.assert_not_called()
    logger.info.assert_not_called()


@pytest.mark.parametrize("options, namespace", [
    ({}, "library"),
    ({"namespace": "test"}, "test"),
], ids=[
    "simple",
    "with-namespace",
])
def test_fetch_existing(mocked_wiz_fetch_definition, options, namespace):
    """Fetch existing definition in definition mapping."""
    result = qip.definition.fetch_existing(
        {"key": "foo", "version": "0.1.0"}, "__MAPPING__", **options
    )
    mocked_wiz_fetch_definition.assert_called_once_with(
        "{0}::foo==0.1.0".format(namespace), "__MAPPING__"
    )
    assert result == mocked_wiz_fetch_definition.return_value


@pytest.mark.parametrize("options, namespace", [
    ({}, "library"),
    ({"namespace": "test"}, "test"),
], ids=[
    "simple",
    "with-namespace",
])
def test_fetch_existing_empty(mocked_wiz_fetch_definition, options, namespace):
    """Fail to fetch existing definition in definition mapping."""
    mocked_wiz_fetch_definition.side_effect = (
        wiz.exception.RequestNotFound("Error!")
    )

    result = qip.definition.fetch_existing(
        {"key": "foo", "version": "0.1.0"}, "__MAPPING__", **options
    )
    mocked_wiz_fetch_definition.assert_called_once_with(
        "{0}::foo==0.1.0".format(namespace), "__MAPPING__"
    )
    assert result is None


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
    assert result.data() == {
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
                    "python >= 2.8, <2.9",
                ]
            }
        ]
    }

    logger.info.assert_called_once_with(
        "\tWiz definition created for 'Foo-0.2.3'."
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
    assert result.data() == {
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
                    "python >= 2.8, <2.9",
                ]
            }
        ]
    }

    logger.info.assert_called_once_with(
        "\tWiz definition created for 'Foo-0.2.3'."
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
    assert result.data() == {
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
                    "python >= 2.8, <2.9",
                    "library::bim[2.8] >=3, <4",
                    "library::bar[2.8]",
                ]
            }
        ]
    }

    logger.info.assert_called_once_with(
        "\tWiz definition created for 'Foo-0.2.3'."
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
    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }

    logger.info.assert_called_once_with(
        "\tWiz definition created for 'Foo-0.2.3'."
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
    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }

    logger.info.assert_called_once_with(
        "\tWiz definition created for 'Foo-0.2.3'."
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
            {
                "identifier": "variant",
            },
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.8",
                "environ": {"KEY28": "VALUE28"},
                "requirements": [
                    "library::bim[2.8] >= 3, < 4",
                    "library::baz"
                ]
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
    )
    assert result.data() == {
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
                    "library::bim[2.8] >= 3, < 4",
                    "library::baz",
                    "python >= 2.8, <2.9",
                    "library::bar[2.8]",
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
    }

    logger.info.assert_called_once_with(
        "\tWiz definition created for 'Foo-0.2.3'."
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
            {
                "identifier": "variant",
            },
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
    )
    assert result.data() == {
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
                    "python >= 2.8, <2.9",
                    "library::bim[2.8] >=3, <4",
                    "library::bar[2.8]",
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
    }

    logger.info.assert_called_once_with(
        "\tWiz definition created for 'Foo-0.2.3'."
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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


def test_update_with_pythonpath():
    """Update definition with existing PYTHONPATH from mapping."""
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "environ": {
            "PYTHONPATH": "/path/to/somewhere:${PYTHONPATH}"
        }
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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "install-root": "/packages",
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:/path/to/somewhere:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "2.8",
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


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

    result = qip.definition.update(
        definition, mapping, "/packages", editable_mode=True
    )

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


def test_update_with_variants_1():
    """Update definition with existing variants.

    Existing Variants are not adding to current variant.

    """
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "variants": [
            {
                "identifier": "variant",
            },
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.8",
                "environ": {"KEY28": "VALUE28"}
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                "environ": {
                    "KEY28": "VALUE28"
                },
                "requirements": [
                    "python >= 2.8, <2.9"
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
    }


def test_update_with_variants_2():
    """Update definition with existing variants.

    Additional variants are not adding to current variant.

    """
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "variants": [
            {
                "identifier": "variant",
            },
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
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

    result = qip.definition.update(definition, mapping, "/packages")

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
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
    }


def test_update_with_additional_variants_1():
    """Update definition with mapping with additional variants.

    Additional variants are adding to current variant.

    """
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

    result = qip.definition.update(
        definition, mapping, "/packages",
        additional_variants=[
            {
                "identifier": "variant",
            },
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.8",
                "environ": {"KEY28": "VALUE28"}
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
    )

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
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
    }


def test_update_with_additional_variants_2():
    """Update definition with mapping with additional variants.

    Additional variants are not adding to current variant.

    """
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

    result = qip.definition.update(
        definition, mapping, "/packages",
        additional_variants=[
            {
                "identifier": "variant",
            },
            {
                "identifier": "3.6",
                "environ": {"KEY36": "VALUE36"}
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
    )

    assert result.data() == {
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
                    "python >= 2.8, <2.9"
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
    }


def test_update_with_additional_variants_3():
    """Update definition with mapping with additional variants.

    Definition to update has existing variants which are not conflicting with
    additional variants.

    """
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "variants": [
            {
                "identifier": "2.8",
                "environ": {"KEY28": "VALUE28"}
            },
        ]
    })

    mapping = {
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    result = qip.definition.update(
        definition, mapping, "/packages",
        additional_variants=[
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
    )

    assert result.data() == {
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
                "environ": {"KEY28": "VALUE28"},
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >= 2.8, <2.9"
                ]
            },
            {
                "identifier": "2.7",
                "environ": {"KEY22": "VALUE22"}
            }
        ]
    }


def test_update_with_additional_variants_4():
    """Update definition with mapping with additional variants.

    Definition to update has existing variants which are conflicting with
    additional variants.

    """
    definition = wiz.definition.Definition({
        "identifier": "foo",
        "version": "0.2.3",
        "namespace": "plugin",
        "description": "This is a library",
        "variants": [
            {
                "identifier": "2.8",
                "environ": {"KEY1": "VALUE1", "KEY2": "VALUE2"}
            },
        ]
    })

    mapping = {
        "target": "Foo/Foo-0.2.3",
        "python": {
            "identifier": "2.8",
            "request": "python >= 2.8, <2.9",
            "library-path": "lib/python2.8/site-packages"
        },
    }

    result = qip.definition.update(
        definition, mapping, "/packages",
        additional_variants=[
            {
                "identifier": "2.8",
                "environ": {
                    "KEY2": "VALUE22",
                    "KEY3": "VALUE3",
                }
            }
        ]
    )

    assert result.data() == {
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
                "environ": {
                    "KEY1": "VALUE1",
                    "KEY2": "VALUE2",
                    "KEY3": "VALUE3",
                },
                "install-location": (
                    "${INSTALL_ROOT}/Foo/Foo-0.2.3/lib/python2.8/site-packages"
                ),
                "requirements": [
                    "python >= 2.8, <2.9"
                ]
            }
        ]
    }


@pytest.mark.parametrize("identifier1, identifier2, expected", [
    ("2.7", "3.6", 1),
    ("3.6", "2.7", -1),
    ("abc", "def", -1),
    ("def", "abc", 1),
    ("2.7", "abc", -1),
    ("abc", "2.7", 1),
    ("2.7", "2.7", 0),
], ids=[
    "float",
    "float-inv",
    "string",
    "string-inv",
    "float-right",
    "float-left",
    "identical",
])
def test_compare_variants(identifier1, identifier2, expected):
    """Compare identifier values from variant mappings."""
    variant1 = {"identifier": identifier1}
    variant2 = {"identifier": identifier2}

    assert qip.definition._compare_variants(variant1, variant2) == expected

    # If result is -1, variant order stays the same.
    if expected == -1:
        assert sorted(
            [variant1, variant2],
            key=functools.cmp_to_key(qip.definition._compare_variants)
        ) == [variant1, variant2]

    # If result is 1, variant order is inverted.
    if expected == 1:
        assert sorted(
            [variant1, variant2],
            key=functools.cmp_to_key(qip.definition._compare_variants)
        ) == [variant2, variant1]
