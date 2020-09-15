# :coding: utf-8

import sys
import os
import tempfile

import pytest
from six.moves import reload_module
from click.testing import CliRunner
import wiz
import wiz.config

import qip.command_line


@pytest.fixture(autouse=True)
def reset_configuration(mocker):
    """Ensure that no personal configuration is fetched during tests."""
    mocker.patch.object(os.path, "expanduser", return_value="__HOME__")

    # Mock temporary directory path before reloading module to reset default
    # values.
    mocker.patch.object(tempfile, "gettempdir", return_value="/tmp")

    # Reset configuration.
    qip.command_line._CONFIG = wiz.config.fetch(refresh=True)
    reload_module(qip.command_line)


@pytest.fixture()
def mocked_install(mocker):
    """Return mocked 'qip.install' function."""
    return mocker.patch.object(qip, "install")


@pytest.fixture()
def mocked_fetch_definition_mapping(mocker):
    """Return mocked 'wiz.fetch_definition_mapping' function."""
    return mocker.patch.object(wiz, "fetch_definition_mapping")


def test_no_arguments(mocked_install, mocked_fetch_definition_mapping):
    """Print help when called with no arguments."""
    runner = CliRunner()
    result = runner.invoke(qip.command_line.main)
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_not_called()
    mocked_fetch_definition_mapping.assert_not_called()


def test_install_no_arguments(mocked_install, mocked_fetch_definition_mapping):
    """Raise error for no arguments on install."""
    runner = CliRunner()

    result = runner.invoke(qip.command_line.install)
    assert result.exit_code == 2
    assert result.exception

    mocked_install.assert_not_called()
    mocked_fetch_definition_mapping.assert_not_called()


def test_missing_output(mocked_install, mocked_fetch_definition_mapping):
    """Error when user does not specify and output directory"""
    runner = CliRunner()

    runner.invoke(qip.command_line.install, ["test"])
    mocked_install.assert_called_once_with(
        ("test",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=False,
        overwrite=None,
        python_target=sys.executable,
        definition_mapping=None
    )
    mocked_fetch_definition_mapping.assert_not_called()


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
def test_install_packages(
    mocked_install, mocked_fetch_definition_mapping, packages
):
    """Install packages."""
    runner = CliRunner()
    result = runner.invoke(qip.command_line.install, list(packages))
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        packages, os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=False,
        overwrite=None,
        python_target=sys.executable,
        definition_mapping=None
    )
    mocked_fetch_definition_mapping.assert_not_called()


def test_install_package_with_custom_paths(
    mocked_install, mocked_fetch_definition_mapping
):
    """Install packages with custom output paths."""
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "-o", "/path1", "-d", "/path2"]
    )
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        ("foo",), "/path1",
        definition_path="/path2",
        editable_mode=False,
        no_dependencies=False,
        overwrite=None,
        python_target=sys.executable,
        definition_mapping=None
    )
    mocked_fetch_definition_mapping.assert_not_called()


def test_install_package_without_dependencies(
    mocked_install, mocked_fetch_definition_mapping
):
    """Install packages without dependencies."""
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--no-dependencies"]
    )
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        ("foo",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=True,
        overwrite=None,
        python_target=sys.executable,
        definition_mapping=None
    )
    mocked_fetch_definition_mapping.assert_not_called()


def test_install_package_overwrite(
    mocked_install, mocked_fetch_definition_mapping
):
    """Install packages overwriting previous package installed."""
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--overwrite-installed"]
    )
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        ("foo",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=False,
        overwrite=True,
        python_target=sys.executable,
        definition_mapping=None
    )
    mocked_fetch_definition_mapping.assert_not_called()


def test_install_package_skip(
    mocked_install, mocked_fetch_definition_mapping
):
    """Install packages skipping previous package installed."""
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--skip-installed"]
    )
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        ("foo",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=False,
        overwrite=False,
        python_target=sys.executable,
        definition_mapping=None
    )
    mocked_fetch_definition_mapping.assert_not_called()


def test_install_package_editable(
    mocked_install, mocked_fetch_definition_mapping
):
    """Install packages in editable mode."""
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--editable"]
    )
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        ("foo",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=True,
        no_dependencies=False,
        overwrite=None,
        python_target=sys.executable,
        definition_mapping=None
    )
    mocked_fetch_definition_mapping.assert_not_called()


def test_install_package_update(
    mocked_install, mocked_fetch_definition_mapping
):
    """Install packages in editable mode."""
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--update"]
    )
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_called_once_with(
        ("foo",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=False,
        overwrite=None,
        python_target=sys.executable,
        definition_mapping="__MAPPING__"
    )
    mocked_fetch_definition_mapping.assert_called_once_with(
        [os.path.join("/tmp", "qip", "definitions")]
    )
