# :coding: utf-8

import re

import pytest

import qip.command
import qip.system
import qip.environ
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
def mocked_extract_key(mocker):
    """Return mocked 'extract_key' function"""
    return mocker.patch.object(qip.package, "extract_key")


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


@pytest.mark.parametrize("package, expected", [
    ("foo", "foo"),
    ("foo==0.1.0", "foo==0.1.0"),
    ("foo >= 7, < 8", "foo >= 7, < 8"),
    ("git@host:user/foo.git", "git+ssh://git@host/user/foo.git"),
    ("git@host1:bar/foo.git@0.1.0", "git+ssh://git@host1/bar/foo.git@0.1.0"),
    (
        "git@github.com:username/foo.git@dev",
        "git+ssh://git@github.com/username/foo.git@dev"
    ),
], ids=[
    "foo",
    "foo==0.1.0",
    "foo >= 7, < 8",
    "git@host:user/foo.git",
    "git@host1:bar/foo.git@0.1.0",
    "git@github.com:username/foo.git@dev"
])
def test_install(
    mocked_fetch_mapping_from_environ, mocked_command_execute, package, expected
):
    """Install package."""
    mocked_fetch_mapping_from_environ.return_value = {}
    mocked_command_execute.return_value = "Installing collected packages: foo"

    result = qip.package.install(
        package, "/path", {"environ": "__ENV__"}, "/cache"
    )
    mocked_fetch_mapping_from_environ.assert_called_once_with(
        "foo", {"environ": "__ENV__"}, extra_keywords=[]
    )
    assert result == {"request": expected, "extra": []}


def test_install_fail(mocked_command_execute):
    """Install package fails on pip install."""
    mocked_command_execute.return_value = "__FAIL__"

    with pytest.raises(ValueError) as error:
        qip.package.install("foo", "/path", {"environ": "__ENV__"}, "/cache")
    assert str(error.value) == "Package name could not be extracted from 'foo'."


def test_fetch_mapping_from_environ(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_extract_key, mocked_is_system_required,
    mocked_extract_command_mapping, mocked_extract_target_path,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment."""
    context = {
        "environ": "__ENV__",
        "python": {
            "identifier": "2.8"
        }
    }

    package = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "0.1.0"
    }

    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": package,
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_extract_key.return_value = "foo"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"

    mapping = qip.package.fetch_mapping_from_environ("foo", context)
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "module_name": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "2.8"
        },
        "target": "/path/to/target"
    }

    mocked_command_execute.assert_called_once_with(
        "python -m pip show --disable-pip-version-check 'foo' -v", "__ENV__",
        quiet=True
    )
    mocked_system_query.assert_not_called()
    mocked_extract_identifier.assert_called_once_with(
        package, extra_keywords=None
    )
    mocked_extract_key.assert_called_once_with(
        package, extra_keywords=None
    )


def test_fetch_mapping_from_environ_with_extra(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_extract_key, mocked_is_system_required,
    mocked_extract_command_mapping, mocked_extract_target_path,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with extra keywords."""
    context = {
        "environ": "__ENV__",
        "python": {
            "identifier": "2.8"
        }
    }

    package = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "0.1.0"
    }

    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": package,
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-doc-test-0.1.0"
    mocked_extract_key.return_value = "foo-doc-test"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"

    mapping = qip.package.fetch_mapping_from_environ(
        "foo", context, extra_keywords=["doc", "test"]
    )
    assert mapping == {
        "identifier": "Foo-doc-test-0.1.0",
        "key": "foo-doc-test",
        "name": "Foo",
        "module_name": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "2.8"
        },
        "target": "/path/to/target"
    }

    mocked_command_execute.assert_called_once_with(
        "python -m pip show --disable-pip-version-check 'foo' -v", "__ENV__",
        quiet=True
    )
    mocked_system_query.assert_not_called()
    mocked_extract_identifier.assert_called_once_with(
        package, extra_keywords=["doc", "test"]
    )
    mocked_extract_key.assert_called_once_with(
        package, extra_keywords=["doc", "test"]
    )


def test_fetch_mapping_from_environ_with_system(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_extract_key, mocked_is_system_required,
    mocked_extract_command_mapping, mocked_extract_target_path,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with system."""
    context = {
        "environ": "__ENV__",
        "python": {
            "identifier": "2.8"
        }
    }

    package = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "0.1.0"
    }

    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": package,
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_extract_key.return_value = "foo"
    mocked_is_system_required.return_value = True
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"
    mocked_system_query.return_value = {"os": "__SYSTEM__"}

    mapping = qip.package.fetch_mapping_from_environ("foo", context)
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "module_name": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "2.8"
        },
        "target": "/path/to/target",
        "system": {"os": "__SYSTEM__"}
    }

    mocked_command_execute.assert_called_once_with(
        "python -m pip show --disable-pip-version-check 'foo' -v", "__ENV__",
        quiet=True
    )
    mocked_system_query.assert_called_once()
    mocked_extract_identifier.assert_called_once_with(
        package, extra_keywords=None
    )
    mocked_extract_key.assert_called_once_with(
        package, extra_keywords=None
    )


def test_fetch_mapping_from_environ_with_description(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_extract_key, mocked_is_system_required,
    mocked_extract_command_mapping, mocked_extract_target_path,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with description."""
    context = {
        "environ": "__ENV__",
        "python": {
            "identifier": "2.8"
        }
    }

    package = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "0.1.0"
    }

    mocked_command_execute.return_value = "Summary: This is a test"
    mocked_extract_dependency_mapping.return_value = {
        "package": package,
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_extract_key.return_value = "foo"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"

    mapping = qip.package.fetch_mapping_from_environ("foo", context)
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "module_name": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "2.8"
        },
        "target": "/path/to/target",
        "description": "This is a test"
    }

    mocked_command_execute.assert_called_once_with(
        "python -m pip show --disable-pip-version-check 'foo' -v", "__ENV__",
        quiet=True
    )
    mocked_system_query.assert_not_called()
    mocked_extract_identifier.assert_called_once_with(
        package, extra_keywords=None
    )
    mocked_extract_key.assert_called_once_with(
        package, extra_keywords=None
    )


def test_fetch_mapping_from_environ_with_location(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_extract_key, mocked_is_system_required,
    mocked_extract_command_mapping, mocked_extract_target_path,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with location."""
    context = {
        "environ": "__ENV__",
        "python": {
            "identifier": "2.8"
        }
    }

    package = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "0.1.0"
    }

    mocked_command_execute.return_value = "Location: /path/to/package"
    mocked_extract_dependency_mapping.return_value = {
        "package": package,
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_extract_key.return_value = "foo"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"

    mapping = qip.package.fetch_mapping_from_environ("foo", context)
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "module_name": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "2.8"
        },
        "target": "/path/to/target",
        "location": "/path/to/package"
    }

    mocked_command_execute.assert_called_once_with(
        "python -m pip show --disable-pip-version-check 'foo' -v", "__ENV__",
        quiet=True
    )
    mocked_system_query.assert_not_called()
    mocked_extract_identifier.assert_called_once_with(
        package, extra_keywords=None
    )
    mocked_extract_key.assert_called_once_with(
        package, extra_keywords=None
    )


def test_fetch_mapping_from_environ_with_commands(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_extract_key, mocked_is_system_required,
    mocked_extract_command_mapping, mocked_extract_target_path,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with commands."""
    context = {
        "environ": "__ENV__",
        "python": {
            "identifier": "2.8"
        }
    }

    package = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "0.1.0"
    }

    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": package,
        "requirements": []
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_extract_key.return_value = "foo"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {"foo": "python -m foo"}
    mocked_extract_target_path.return_value = "/path/to/target"

    mapping = qip.package.fetch_mapping_from_environ("foo", context)
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "module_name": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "2.8"
        },
        "target": "/path/to/target",
        "command": {"foo": "python -m foo"}
    }

    mocked_command_execute.assert_called_once_with(
        "python -m pip show --disable-pip-version-check 'foo' -v", "__ENV__",
        quiet=True
    )
    mocked_system_query.assert_not_called()
    mocked_extract_identifier.assert_called_once_with(
        package, extra_keywords=None
    )
    mocked_extract_key.assert_called_once_with(
        package, extra_keywords=None
    )


def test_fetch_mapping_from_environ_with_requirements(
    mocked_extract_dependency_mapping, mocked_extract_identifier,
    mocked_extract_key, mocked_is_system_required,
    mocked_extract_command_mapping, mocked_extract_target_path,
    mocked_command_execute, mocked_system_query
):
    """Return a package mapping from environment with requirements."""
    context = {
        "environ": "__ENV__",
        "python": {
            "identifier": "2.8"
        }
    }

    package = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "0.1.0"
    }

    mocked_command_execute.return_value = ""
    mocked_extract_dependency_mapping.return_value = {
        "package": package,
        "requirements": [
            "bim >= 0.1.0, < 1",
            "baz",
        ]
    }

    mocked_extract_identifier.return_value = "Foo-0.1.0"
    mocked_extract_key.return_value = "foo"
    mocked_is_system_required.return_value = False
    mocked_extract_command_mapping.return_value = {}
    mocked_extract_target_path.return_value = "/path/to/target"

    mapping = qip.package.fetch_mapping_from_environ("foo", context)
    assert mapping == {
        "identifier": "Foo-0.1.0",
        "key": "foo",
        "name": "Foo",
        "module_name": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "2.8"
        },
        "target": "/path/to/target",
        "requirements": [
            "bim >= 0.1.0, < 1",
            "baz"
        ]
    }

    mocked_command_execute.assert_called_once_with(
        "python -m pip show --disable-pip-version-check 'foo' -v", "__ENV__",
        quiet=True
    )
    mocked_system_query.assert_not_called()
    mocked_extract_identifier.assert_called_once_with(
        package, extra_keywords=None
    )
    mocked_extract_key.assert_called_once_with(
        package, extra_keywords=None
    )


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

    mapping = qip.package.extract_dependency_mapping(
        "foo", {}, extra_keywords=["doc", "test"]
    )
    mocked_command_execute.assert_called_once_with(mocker.ANY, {}, quiet=True)
    assert re.match(
        r"python .+ foo\[doc,test]",
        mocked_command_execute.call_args_list[0][0][0]
    )
    assert mapping == {"package": {"key": "foo"}}


def test_extract_dependency_mapping_fail_tree(mocked_command_execute):
    """Fail to return package mapping if pip_query returns nothing."""
    mocked_command_execute.return_value = ""

    with pytest.raises(RuntimeError) as error:
        qip.package.extract_dependency_mapping("foo", {})

    assert str(error.value) == "Impossible to fetch installed package for 'foo'"


def test_extract_identifier():
    """Return identifier from package mapping."""
    mapping = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "1.11",
    }
    identifier = qip.package.extract_identifier(mapping)
    assert identifier == "Foo-1.11"


def test_extract_identifier_with_extra():
    """Return identifier computed with extra keywords."""
    mapping = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "1.11",
    }
    identifier = qip.package.extract_identifier(
        mapping, extra_keywords=["doc", "test"]
    )
    assert identifier == "Foo-doc-test-1.11"


def test_extract_key():
    """Return key from package mapping."""
    mapping = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "1.11",
    }
    identifier = qip.package.extract_key(mapping)
    assert identifier == "foo"


def test_extract_key_with_extra():
    """Return key from package mapping with extra keywords."""
    mapping = {
        "key": "foo",
        "package_name": "Foo",
        "module_name": "foo",
        "installed_version": "1.11",
    }
    identifier = qip.package.extract_key(
        mapping, extra_keywords=["doc", "test"]
    )
    assert identifier == "foo-doc-test"


@pytest.mark.parametrize("metadata, expected", [
    ("", False),
    ("Operating System :: OS Independent", False),
    (
        (
            "Operating System :: OS Independent"
            "Operating System :: Linux"
        ),
        True
    ),
    (
        (
            "Operating System :: Mac"
            "Operating System :: Linux"
        ),
        True
    ),
    (
        (
            "Operating System :: Mac"
        ),
        True
    ),
], ids=[
    "no-metadata",
    "independent",
    "confusing-classifiers",
    "multi-platforms",
    "single-platform",
])
def test_is_system_required(metadata, expected):
    """Indicate whether package is platform-specific."""
    assert qip.package.is_system_required(metadata) == expected


@pytest.mark.parametrize("metadata, expected", [
    ("", {}),
    (
        (
            "Entry-points:\n"
            "  [console_scripts]\n"
            "  sphinx-apidoc = sphinx.ext.apidoc:main\n"
            "  sphinx-autogen = sphinx.ext.autosummary.generate:main\n"
            "  sphinx-build = sphinx.cmd.build:main\n"
            "  sphinx-quickstart = sphinx.cmd.quickstart:main\n"
        ),
        {
            "sphinx-apidoc": "python -m sphinx.ext.apidoc",
            "sphinx-autogen": "python -m sphinx.ext.autosummary.generate",
            "sphinx-build": "python -m sphinx.cmd.build",
            "sphinx-quickstart": "python -m sphinx.cmd.quickstart",
        }
    ),
    (
        (
            "Entry-points:\n"
            "  [console_scripts]\n"
            "  qip = qip.__main__:main\n"
        ),
        {
            "qip": "python -m qip"
        }
    ),
], ids=[
    "no-metadata",
    "multi-commands",
    "main-command",
])
def test_extract_command_mapping(metadata, expected):
    """Extract command mapping from entry points"""
    assert qip.package.extract_command_mapping(metadata) == expected


def test_extract_command_mapping_with_extra():
    """Extract command mapping from entry points with extra keywords"""
    metadata = (
        "Entry-points:\n"
        "  [console_scripts]\n"
        "  foo = foo.__main__:main [test]\n"
        "  bar = bar.__main__:main [doc]\n"
    )

    assert qip.package.extract_command_mapping(metadata) == {}

    assert qip.package.extract_command_mapping(
        metadata, extra_keywords=["test"]
    ) == {
        "foo": "python -m foo"
    }

    assert qip.package.extract_command_mapping(
        metadata, extra_keywords=["doc"]
    ) == {
        "bar": "python -m bar"
    }

    assert qip.package.extract_command_mapping(
        metadata, extra_keywords=["doc", "test"]
    ) == {
        "foo": "python -m foo",
        "bar": "python -m bar"
    }


def test_extract_target_path():
    """Return the corresponding target path from package."""
    path = qip.package.extract_target_path("Foo", "Foo-0.1.0", "2.8")
    assert path == "Foo/Foo-0.1.0-py28"


def test_extract_target_path_with_system():
    """Return the corresponding target path from package with system."""
    path = qip.package.extract_target_path(
        "Foo", "Foo-0.1.0", "2.8", os_mapping={
            "name": "centos",
            "major_version": 7
        }
    )
    assert path == "Foo/Foo-0.1.0-py28-centos7"
