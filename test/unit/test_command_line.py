# :coding: utf-8

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
    expected = ("Usage: install [OPTIONS] REQUESTS...\n\n"
                "Error: Missing argument \"requests\".\n")

    result = runner.invoke(qip.command_line.install)
    assert result.exit_code == 2
    assert result.exception
    assert result.output == expected


def test_missing_output():
    """Error when user does not specify and output directory"""
    runner = CliRunner()
    expected = (
        "Usage: install [OPTIONS] REQUESTS...\n\n"
        "Error: Missing option \"-o\" / \"--output-path\".\n"
    )

    result = runner.invoke(qip.command_line.install, ["test"])
    assert result.exit_code == 2
    assert result.exception
    assert result.output == expected


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
        definition_path=None,
        editable_mode=False,
        no_dependencies=False,
        overwrite_packages=None
    )