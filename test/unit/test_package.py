# :coding: utf-8

import re

import pytest

import qip.command
import qip.system
import qip.package


@pytest.fixture()
def mocked_system_query(mocker):
    """Return mocked command execute."""
    return mocker.patch.object(qip.system, "query")


@pytest.fixture()
def mocked_command_execute(mocker):
    """Return mocked command execute."""
    return mocker.patch.object(qip.command, "execute")


@pytest.fixture()
def mocked_fetch_mapping_from_environ(mocker):
    """Return mocked 'fetch_mapping_from_environ' function"""
    return mocker.patch.object(qip.package, "fetch_mapping_from_environ")


@pytest.fixture()
def mocked_extract_dependency_mapping(mocker):
    """Return mocked 'extract_dependency_mapping' function"""
    return mocker.patch.object(qip.package, "extract_dependency_mapping")


@pytest.fixture()
def mocked_extract_identifier(mocker):
    """Return mocked 'extract_identifier' function"""
    return mocker.patch.object(qip.package, "extract_identifier")


@pytest.fixture()
def mocked_is_system_required(mocker):
    """Return mocked 'is_system_required' function"""
    return mocker.patch.object(qip.package, "is_system_required")


@pytest.fixture()
def mocked_extract_command_mapping(mocker):
    """Return mocked 'extract_command_mapping' function"""
    return mocker.patch.object(qip.package, "extract_command_mapping")


@pytest.fixture()
def mocked_extract_target_path(mocker):
    """Return mocked 'extract_target_path' function"""
    return mocker.patch.object(qip.package, "extract_target_path")


@pytest.fixture()
def mocked_fetch_python_request_mapping(mocker):
    """Return mocked 'fetch_python_request_mapping' function"""
    return mocker.patch.object(qip.package, "fetch_python_request_mapping")


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
def test_install(
        mocked_fetch_mapping_from_environ, mocked_command_execute, package
):
    """Install package."""
    mocked_fetch_mapping_from_environ.return_value = "__VALUE__"
    mocked_command_execute.return_value = "Installing collected packages: foo"

    result = qip.package.install(package, "/path", {}, "/cache")
    mocked_fetch_mapping_from_environ.assert_called_once_with(
        "foo", {}, extra=None
    )
    assert result == "__VALUE__"


def test_install_fail(mocked_command_execute):
    """Install package fails on pip install."""
    mocked_command_execute.return_value = "__FAIL__"

    with pytest.raises(ValueError) as error:
        qip.package.install("foo", "/path", {}, "/cache")
    assert str(error.value) == "Package name could not be extracted from 'foo'."


def test_fetch_mapping_from_environ(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_is_system_required, mocked_extract_command_mapping,
    mocked_extract_target_path, mocked_fetch_python_request_mapping,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment."""
    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "0.1.0"
        },
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"
    mocked_fetch_python_request_mapping.return_value = "__PYTHON__"

    mapping = qip.package.fetch_mapping_from_environ("foo", {})
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "version": "0.1.0",
        "python": "__PYTHON__",
        "target": "/path/to/target"
    }

    mocked_command_execute.assert_called_once_with(
        "pip show --disable-pip-version-check 'foo' -v", {}, quiet=True
    )
    mocked_system_query.assert_not_called()


def test_fetch_mapping_from_environ_with_system(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_is_system_required, mocked_extract_command_mapping,
    mocked_extract_target_path, mocked_fetch_python_request_mapping,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with system."""
    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "0.1.0"
        },
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_is_system_required.return_value = True
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"
    mocked_fetch_python_request_mapping.return_value = "__PYTHON__"
    mocked_system_query.return_value = {"os": "__SYSTEM__"}

    mapping = qip.package.fetch_mapping_from_environ("foo", {})
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "version": "0.1.0",
        "python": "__PYTHON__",
        "target": "/path/to/target",
        "system": {"os": "__SYSTEM__"}
    }

    mocked_command_execute.assert_called_once_with(
        "pip show --disable-pip-version-check 'foo' -v", {}, quiet=True
    )
    mocked_system_query.assert_called_once()


def test_fetch_mapping_from_environ_with_description(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_is_system_required, mocked_extract_command_mapping,
    mocked_extract_target_path, mocked_fetch_python_request_mapping,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with description."""
    mocked_command_execute.return_value = "Summary: This is a test"
    mocked_extract_dependency_mapping.return_value = {
        "package": {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "0.1.0"
        },
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"
    mocked_fetch_python_request_mapping.return_value = "__PYTHON__"

    mapping = qip.package.fetch_mapping_from_environ("foo", {})
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "version": "0.1.0",
        "python": "__PYTHON__",
        "target": "/path/to/target",
        "description": "This is a test"
    }

    mocked_command_execute.assert_called_once_with(
        "pip show --disable-pip-version-check 'foo' -v", {}, quiet=True
    )
    mocked_system_query.assert_not_called()


def test_fetch_mapping_from_environ_with_location(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_is_system_required, mocked_extract_command_mapping,
    mocked_extract_target_path, mocked_fetch_python_request_mapping,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with location."""
    mocked_command_execute.return_value = "Location: /path/to/package"
    mocked_extract_dependency_mapping.return_value = {
        "package": {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "0.1.0"
        },
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"
    mocked_fetch_python_request_mapping.return_value = "__PYTHON__"

    mapping = qip.package.fetch_mapping_from_environ("foo", {})
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "version": "0.1.0",
        "python": "__PYTHON__",
        "target": "/path/to/target",
        "location": "/path/to/package"
    }

    mocked_command_execute.assert_called_once_with(
        "pip show --disable-pip-version-check 'foo' -v", {}, quiet=True
    )
    mocked_system_query.assert_not_called()


def test_fetch_mapping_from_environ_with_commands(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_is_system_required, mocked_extract_command_mapping,
    mocked_extract_target_path, mocked_fetch_python_request_mapping,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with commands."""
    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "0.1.0"
        },
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {"foo": "python -m foo"}
    mocked_extract_target_path.return_value = "/path/to/target"
    mocked_fetch_python_request_mapping.return_value = "__PYTHON__"

    mapping = qip.package.fetch_mapping_from_environ("foo", {})
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "version": "0.1.0",
        "python": "__PYTHON__",
        "target": "/path/to/target",
        "command": {"foo": "python -m foo"}
    }

    mocked_command_execute.assert_called_once_with(
        "pip show --disable-pip-version-check 'foo' -v", {}, quiet=True
    )
    mocked_system_query.assert_not_called()


def test_fetch_mapping_from_environ_with_requirements(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_is_system_required, mocked_extract_command_mapping,
    mocked_extract_target_path, mocked_fetch_python_request_mapping,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with requirements."""
    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "0.1.0"
        },
        "requirements": [
            "bim >= 0.1.0, < 1",
            "baz",
        ]
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"
    mocked_fetch_python_request_mapping.return_value = "__PYTHON__"

    mapping = qip.package.fetch_mapping_from_environ("foo", {})
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "version": "0.1.0",
        "python": "__PYTHON__",
        "target": "/path/to/target",
        "requirements": [
            "bim >= 0.1.0, < 1",
            "baz"
        ]
    }

    mocked_command_execute.assert_called_once_with(
        "pip show --disable-pip-version-check 'foo' -v", {}, quiet=True
    )
    mocked_system_query.assert_not_called()


def test_extract_dependency_mapping(mocker, mocked_command_execute):
    """Return package mapping from dependency mapping."""
    mocked_command_execute.return_value = "{\"package\": {\"key\": \"foo\"}}"

    mapping = qip.package.extract_dependency_mapping("foo", {})

    mocked_command_execute.assert_called_once_with(mocker.ANY, {}, quiet=True)
    assert re.match(
        "python .+ foo", mocked_command_execute.call_args_list[0][0][0]
    )
    assert mapping == {"package": {"key": "foo"}}


def test_extract_dependency_mapping_with_extra(mocker, mocked_command_execute):
    """Return package mapping from dependency mapping with extra requirements.
    """
    mocked_command_execute.return_value = "{\"package\": {\"key\": \"foo\"}}"

    mapping = qip.package.extract_dependency_mapping("foo", {}, extra="dev")
    mocked_command_execute.assert_called_once_with(mocker.ANY, {}, quiet=True)
    assert re.match(
        r"python .+ foo\[dev\]", mocked_command_execute.call_args_list[0][0][0]
    )
    assert mapping == {"package": {"key": "foo"}}


def test_extract_dependency_mapping_fail_tree(mocked_command_execute):
    """Fail to return package mapping if pip_query returns nothing."""
    mocked_command_execute.return_value = ""

    with pytest.raises(RuntimeError) as error:
        qip.package.extract_dependency_mapping("foo", {})

    assert str(error.value) == "Impossible to fetch installed package for 'foo'"


def test_extract_identifier():
    """Return corresponding identifier from package mapping."""
    mapping = {
        "key": "foo",
        "package_name": "Foo",
        "installed_version": "1.11",
    }
    identifier = qip.package.extract_identifier(mapping)
    assert identifier == "Foo-1.11"
