# :coding: utf-8

import re

import pytest

import qip.command
import qip.package


@pytest.fixture()
def mocked_command(mocker):
    """Return mocked command execute."""
    _mocked_command = mocker.patch.object(qip.command, "execute", autospec=True)
    return _mocked_command


@pytest.mark.parametrize("package", [
    "foo",
    "foo==0.1.0",
    "foo >= 7, < 8",
    "git@gitlab:rnd/foo.git",
    "git@gitlab:rnd/foo.git@0.1.0",
    "git@gitlab:rnd/foo.git@dev"
], ids=[
    "foo",
    "foo==0.1.0",
    "foo >= 7, < 8",
    "git@gitlab:rnd/foo.git",
    "git@gitlab:rnd/foo.git@0.1.0",
    "git@gitlab:rnd/foo.git@dev"
])
def test_install(mocker, mocked_command, package):
    """Install package."""
    mocked_fetch_mapping_from_environ = mocker.patch.object(
        qip.package, "fetch_mapping_from_environ"
    )
    mocked_fetch_mapping_from_environ.return_value = "__VALUE__"
    mocked_command.return_value = "Installing collected packages: foo"

    result = qip.package.install(package, "/path", {}, "/cache")
    mocked_fetch_mapping_from_environ.assert_called_once_with(
        "foo", {}, extra=None
    )
    assert result == "__VALUE__"


def test_install_fail(mocked_command):
    """Install package fails on pip install."""
    mocked_command.return_value = "__FAIL__"

    with pytest.raises(ValueError) as error:
        qip.package.install("foo", "/path", {}, "/cache")
    assert str(error.value) == "Package name could not be extracted from 'foo'."


@pytest.mark.parametrize("package, expected", [
    (
        "git@gitlab:rnd/foo.git",
        "git+ssh://git@gitlab/rnd/foo.git"
    ),
    (
        "foo",
        "foo"
    )
], ids=[
    "git",
    "pypi"
])
def test_sanitise_request(package, expected):
    """Replace the gitlab copied prefix with the one for pip"""

    result = qip.package.sanitise_request(package)
    assert result == expected


@pytest.mark.parametrize(
    "name, dependency_mapping, metadata_mapping, expected",
[
    (
        "foo",
        {
            "package": {
                "key": "foo",
                "package_name": "Foo",
                "installed_version": "0.1.0"
            }
        },
        {
            "description": "This is a Python package"
        },
        {
            "identifier": "Foo-0.1.0",
            "name": "Foo",
            "key": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "target": "Foo/Foo-0.1.0"
        }
    ),
    (
        "foo",
        {
            "package": {
                "key": "foo",
                "package_name": "Foo",
                "installed_version": "0.1.0"
            }
        },
        {
            "description": "This is a Python package",
            "system": {
                "platform": "linux",
                "arch": "x86_64",
                "os": {
                    "name": "centos",
                    "major_version": 7
                }
            },
        },
        {
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
            "target": "Foo/Foo-0.1.0-centos7"
        }
    ),
    (
        "foo",
        {
            "package": {
                "key": "foo",
                "package_name": "Foo",
                "installed_version": "0.1.0"
            },
            "dependencies": [
                {
                    "key": "bar",
                    "package_name": "Bar",
                    "required_version": "bar"
                },
                {
                    "key": "bim",
                    "package_name": "Bim",
                    "required_version": "bim >= 2, <3"
                }
            ]
        },
        {
            "description": "This is a Python package",
            "target": "Foo/Foo-0.1.0"
        },
        {
            "identifier": "Foo-0.1.0",
            "name": "Foo",
            "key": "foo",
            "version": "0.1.0",
            "description": "This is a Python package",
            "requirements": [
                "bar",
                "bim >= 2, <3",
            ],
            "target": "Foo/Foo-0.1.0"
        }
    )
], ids=[
    "no-requirements",
    "system",
    "requirements"
])
def test_fetch_mapping_from_environ(
    mocker, name, dependency_mapping, metadata_mapping, expected
):
    """Return a mapping with information about the package."""
    mocker.patch.object(
        qip.package, "extract_dependency_mapping",
        return_value=dependency_mapping
    )
    mocker.patch.object(
        qip.package, "extract_metadata_mapping",
        return_value=metadata_mapping
    )

    mapping = qip.package.fetch_mapping_from_environ(name, {})
    assert mapping == expected


def test_extract_dependency_mapping(mocker, mocked_command):
    """Return package mapping from dependency mapping."""
    mocked_command.return_value = "{\"package\": {\"key\": \"foo\"}}"

    mapping = qip.package.extract_dependency_mapping("foo", {})

    mocked_command.assert_called_once_with(mocker.ANY, {}, quiet=True)
    assert re.match(
        "python .+ foo", mocked_command.call_args_list[0][0][0]
    )
    assert mapping == {"package": {"key": "foo"}}


def test_extract_dependency_mapping_with_extra(mocker, mocked_command):
    """Return package mapping from dependency mapping with extra requirements.
    """
    mocked_command.return_value = "{\"package\": {\"key\": \"foo\"}}"

    mapping = qip.package.extract_dependency_mapping("foo", {}, extra="dev")
    mocked_command.assert_called_once_with(mocker.ANY, {}, quiet=True)
    assert re.match(
        r"python .+ foo\[dev\]", mocked_command.call_args_list[0][0][0]
    )
    assert mapping == {"package": {"key": "foo"}}


def test_extract_dependency_mapping_fail_tree(mocked_command):
    """Fail to return package mapping if pipdeptree returns nothing."""
    mocked_command.return_value = ""

    with pytest.raises(RuntimeError) as error:
        qip.package.extract_dependency_mapping("foo", {})

    assert str(error.value) == "Impossible to fetch installed package for 'foo'"


@pytest.mark.parametrize("name, command_result, expected", [
    (
        "foo",
        (
            "Name: foo\n"
            "Summary: Some description\n"
        ),
        {
            "description": "Some description"
        }
    ),
    (
        "foo",
        (
            "Name: foo\n"
            "Summary: Some description\n"
            "Operating System :: OS Independent\n"
        ),
        {
            "description": "Some description"
        }
    ),
    (
        "foo",
        (
            "Name: foo\n"
            "Summary: Some description\n"
            "Operating System :: Unix\n"
        ),
        {
            "description": "Some description",
            "system": {}
        }
    )
], ids=[
    "description",
    "os-independent",
    "os-dependent"
])
def test_extract_metadata_mapping(
    mocker, mocked_command, name, command_result, expected
):
    """Return package mapping from available metadata."""
    mocker.patch.object(qip.system, "query", return_value={})
    mocked_command.return_value = command_result

    mapping = qip.package.extract_metadata_mapping(name, {})
    assert mapping == expected


def test_extract_identifier():
    """Return corresponding identifier from package mapping."""
    mapping = {
        "key": "foo",
        "package_name": "Foo",
        "installed_version": "1.11",
    }
    identifier = qip.package.extract_identifier(mapping)
    assert identifier == "Foo-1.11"
