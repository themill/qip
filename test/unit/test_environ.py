# :coding: utf-8

import os.path

import pytest
import wiz

import qip.environ


@pytest.fixture()
def mocked_os_isfile(mocker):
    """Return mocked 'wiz.resolve_context' function"""
    return mocker.patch.object(os.path, "isfile")


@pytest.fixture()
def mocked_wiz_resolve_context(mocker):
    """Return mocked 'wiz.resolve_context' function"""
    return mocker.patch.object(wiz, "resolve_context")


def test_fetch_environ(mocked_wiz_resolve_context):
    """Fetch and return environment mapping."""
    mocked_wiz_resolve_context.return_value = {"environ": "__ENVIRON__"}

    environ = qip.environ.fetch("python==2.7.*")
    assert environ == "__ENVIRON__"

    mocked_wiz_resolve_context.assert_called_once_with(
        ["python==2.7.*"], environ_mapping={}
    )


def test_fetch_environ_with_mapping(mocked_wiz_resolve_context):
    """Fetch and return environment mapping with initial mapping."""
    mocked_wiz_resolve_context.return_value = {"environ": "__ENVIRON__"}

    environ = qip.environ.fetch("python==2.7.*", mapping="__INITIAL_MAPPING__")
    assert environ == "__ENVIRON__"

    mocked_wiz_resolve_context.assert_called_once_with(
        ["python==2.7.*"], environ_mapping="__INITIAL_MAPPING__"
    )


def test_fetch_environ_with_python_path(mocked_wiz_resolve_context):
    """Fetch and return environment mapping with python path."""
    mocked_wiz_resolve_context.return_value = {"environ": "__ENVIRON__"}

    environ = qip.environ.fetch("/bin/python")
    assert environ == {
        "PATH": "/bin:${PATH}"
    }

    mocked_wiz_resolve_context.assert_not_called()


def test_python_lib_path():
    """Return relative library destination depending on the Python version."""
    assert qip.environ.python_library_path() == os.path.join(
        "lib", "python2.8", "site-packages"
    )


def test_python_request_mapping():
    """Return mapping indicating the Python version required."""
    assert qip.environ.python_request_mapping() == {
        "identifier": "2.8",
        "request": "python >= 2.8, < 2.9"
    }
