# :coding: utf-8

import sys
import os
import tempfile

import pytest
from six.moves import reload_module
from click.testing import CliRunner
import wiz.registry
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
def mocked_get_defaults_registries(mocker):
    """Return mocked 'wiz.registry.get_defaults' function."""
    return mocker.patch.object(wiz.registry, "get_defaults")


def test_no_arguments(mocked_install, mocked_get_defaults_registries):
    """Print help when called with no arguments."""
    runner = CliRunner()
    result = runner.invoke(qip.command_line.main)
    assert result.exit_code == 0
    assert not result.exception

    mocked_install.assert_not_called()
    mocked_get_defaults_registries.assert_not_called()


def test_install_no_arguments(mocked_install, mocked_get_defaults_registries):
    """Raise error for no arguments on install."""
    runner = CliRunner()

    result = runner.invoke(qip.command_line.install)
    assert result.exit_code == 2
    assert result.exception

    mocked_install.assert_not_called()
    mocked_get_defaults_registries.assert_not_called()


def test_missing_output(mocked_install, mocked_get_defaults_registries):
    """Error when user does not specify and output directory"""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

    runner = CliRunner()
    runner.invoke(qip.command_line.install, ["test"])
    mocked_install.assert_called_once_with(
        ("test",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=False,
        overwrite=None,
        python_target=sys.executable,
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


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
    mocked_install, mocked_get_defaults_registries, packages
):
    """Install packages."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

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
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_package_with_custom_paths(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages with custom output paths."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

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
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_package_without_dependencies(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages without dependencies."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

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
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_package_overwrite(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages overwriting previous package installed."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

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
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_package_skip(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages skipping previous package installed."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

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
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_package_editable(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages in editable mode."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

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
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_package_update_output(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages and consider definition output as a registry."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

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
        registry_paths=[
            "/registry1", "/registry2",
            os.path.join("/tmp", "qip", "definitions")
        ],
        update_existing_definitions=True,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_package_ignore_registries(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages while ignoring default registries."""
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--ignore-registries"]
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
        registry_paths=[],
        update_existing_definitions=False,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_not_called()


def test_install_package_update_and_ignore_registries(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages while considering definition output as a registry and
    ignoring default registries.
    """
    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--ignore-registries", "--update"]
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
        registry_paths=[
            os.path.join("/tmp", "qip", "definitions")
        ],
        update_existing_definitions=True,
        continue_on_error=False
    )
    mocked_get_defaults_registries.assert_not_called()


def test_install_continue_on_error(
    mocked_install, mocked_get_defaults_registries
):
    """Install packages without raising error when package installation fails.
    """
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--continue-on-error"]
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
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=True
    )
    mocked_get_defaults_registries.assert_called_once_with()


def test_install_fails(
    mocked_install, mocked_get_defaults_registries
):
    """Fail to install packages."""
    mocked_get_defaults_registries.return_value = ["/registry1", "/registry2"]
    mocked_install.side_effect = RuntimeError("Oh Shit")

    runner = CliRunner()
    result = runner.invoke(
        qip.command_line.install, ["foo", "--continue-on-error"]
    )
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert (
        "Error: Impossible to resume installation process:\n\nOh Shit"
    ) in result.output

    mocked_install.assert_called_once_with(
        ("foo",), os.path.join("/tmp", "qip", "packages"),
        definition_path=os.path.join("/tmp", "qip", "definitions"),
        editable_mode=False,
        no_dependencies=False,
        overwrite=None,
        python_target=sys.executable,
        registry_paths=["/registry1", "/registry2"],
        update_existing_definitions=False,
        continue_on_error=True
    )
    mocked_get_defaults_registries.assert_called_once_with()
