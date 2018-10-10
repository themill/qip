# :coding: utf-8

import os
import re

import pytest
import wiz

import qip.definition


@pytest.fixture()
def mocked_package_mapping(mocker):
    """Return mocked example package mapping."""
    return {
        "identifier": "Foo-0.1.0",
        "name": "Foo",
        "key": "foo",
        "version": "0.1.0",
        "description": "This is a Python package",
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": {
                "name": "centos",
                "major_version": 7
            }
        },
        "requirements": [
            {
                "identifier": "Bar-0.1.0",
                "request": "bar",
            },
            {
                "identifier": "Bim-2.3.1",
                "request": "bim >= 2, <3",
            }
        ]
    }


@pytest.mark.parametrize("lib_exists, bin_exists, expected", [
    (
        False, False,
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "system": {
                "platform": "linux",
                "arch": "x86_64",
                "os": "centos >= 7, <8"
            },
            "requirements": [
                "bar",
                "bim >= 2, <3"
            ]
        }
    ),
    (
        True, False,
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "system": {
                "platform": "linux",
                "arch": "x86_64",
                "os": "centos >= 7, <8"
            },
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}/lib/python2.7/site-packages:${PYTHONPATH}"
            },
            "requirements": [
                "bar",
                "bim >= 2, <3"
            ]
        }
    ),
    (
        False, True,
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "system": {
                "platform": "linux",
                "arch": "x86_64",
                "os": "centos >= 7, <8"
            },
            "environ": {
                "PATH": "${INSTALL_LOCATION}/bin:${PATH}"
            },
            "requirements": [
                "bar",
                "bim >= 2, <3"
            ]
        }
    ),
    (
        True, True,
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "system": {
                "platform": "linux",
                "arch": "x86_64",
                "os": "centos >= 7, <8"
            },
            "environ": {
                "PATH": "${INSTALL_LOCATION}/bin:${PATH}",
                "PYTHONPATH": "${INSTALL_LOCATION}/lib/python2.7/site-packages:${PYTHONPATH}"
            },
            "requirements": [
                "bar",
                "bim >= 2, <3"
            ]
        }
    )
], ids=[
    "no_environ",
    "add_lib",
    "add_bin",
    "add_lib_and_bin"
])
def test_create(
    mocker, mocked_package_mapping, lib_exists, bin_exists, expected
):
    """Export Wiz definition for package."""
    mocked_isdir = mocker.patch.object(os.path, "isdir")
    mocked_isdir.side_effect = [lib_exists, bin_exists]

    result = qip.definition.create(mocked_package_mapping, "/path")
    assert result == expected


def test_retrieve_does_not_exist(mocker, mocked_package_mapping):
    """Fail to retrieve definition from package install as it does not exist."""
    mocker.patch.object(os.path, "exists", return_value=False)

    result = qip.definition.retrieve(mocked_package_mapping, "/path")
    assert result is None


@pytest.mark.parametrize("original, expected", [
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package"
        }
    ),
    (
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "system": {
                "platform": "linux",
                "arch": "x86_64",
                "os": "centos >= 7, <8"
            },
            "requirements": [
                "bar",
                "bim >=2, <3"
            ]
        },
        {
            "identifier": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "system": {
                "platform": "linux",
                "arch": "x86_64",
                "os": "centos >= 7, <8"
            },
            "requirements": [
                "bar",
                "bim >=2, <3"
            ]
        }
    )
], ids=[
    "example 1",
    "example 2"
])
def test_retrieve(mocker, mocked_package_mapping, original, expected):
    """Retrieve and update definition from package install."""
    mocker.patch.object(os.path, "exists", return_value=True)
    mocker.patch.object(wiz, "load_definition",
        return_value=wiz.definition.Definition(original)
    )

    result = qip.definition.retrieve(mocked_package_mapping, "/path")

    assert result.to_dict(serialize_content=True) == expected
