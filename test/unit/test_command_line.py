# :coding: utf-8

import os
import tempfile

import pytest

import qip.command_line
from click.testing import CliRunner


@pytest.fixture()
def mocked_install(mocker):
    """Return mocked command execute."""
    _mocked_install = mocker.patch.object(qip, "install")
    return _mocked_install


def test_no_arguments():
    """Print help when called with no arguments."""
    runner = CliRunner()
    result = runner.invoke(qip.command_line.main)
    assert result.exit_code == 0
    assert not result.exception


def test_install_no_arguments():
    """Raise error for no arguments on install."""
    runner = CliRunner()
    expected = ("Usage: install [OPTIONS] REQUESTS...\n"
                "Try \"install --help\" for help.\n\n"
                "Error: Missing argument \"REQUESTS...\".\n")

    result = runner.invoke(qip.command_line.install)
    assert result.exit_code == 2
    assert result.exception
    assert result.output == expected


def test_missing_output(mocked_install):
    """Error when user does not specify and output directory"""
    runner = CliRunner()

    runner.invoke(qip.command_line.install, ["test"])
    mocked_install.assert_called_once_with(
        ("test",), os.path.join(tempfile.gettempdir(), "qip", "packages"),
        definition_path=os.path.join(
            tempfile.gettempdir(), "qip", "definitions"
        ),
        editable_mode=False,
        no_dependencies=False,
        overwrite=None
    )


@pytest.mark.parametrize("packages", [
    ("foo",),
    ("foo", "bar"),
    ("foo==0.1.0",),
    ("foo >= 7, < 8",),
    ("git@gitlab:rnd/foo.git",),
    ("git@gitlab:rnd/foo.git@0.1.0",),
    ("git@gitlab:rnd/foo.git@dev",)
], ids=[
    "foo",
    "foo and bar",
    "foo==0.1.0",
    "foo >= 7, < 8",
    "git@gitlab:rnd/foo.git",
    "git@gitlab:rnd/foo.git@0.1.0",
    "git@gitlab:rnd/foo.git@dev"
])
def test_install(mocked_install, packages):
    """Error when user does not specify and output directory"""
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, list(packages) + ["--output-path", "/path"]
    )
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        packages, "/path",
        definition_path=os.path.join(
            tempfile.gettempdir(), "qip", "definitions"
        ),
        editable_mode=False,
        no_dependencies=False,
        overwrite=None
    )
