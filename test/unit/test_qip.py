# :coding: utf-8

import os
import shutil
import tempfile
import wiz

import click
import pytest

import qip
import qip.filesystem
import qip.package
import qip.definition


@pytest.fixture()
def mocked_tempfile_mkdtemp(mocker):
    """Return mocked 'tempfile.mkdtemp' function"""
    return mocker.patch.object(tempfile, "mkdtemp")


@pytest.fixture()
def mocked_shutil_rmtree(mocker):
    """Return mocked 'shutil.rmtree' function"""
    return mocker.patch.object(shutil, "rmtree")


@pytest.fixture()
def mocked_shutil_copytree(mocker):
    """Return mocked 'shutil.copytree' function"""
    return mocker.patch.object(shutil, "copytree")


@pytest.fixture()
def mocked_click_confirm(mocker):
    """Return mocked 'click.confirm' function"""
    return mocker.patch.object(click, "confirm")


@pytest.fixture()
def mocked_copy_to_destination(mocker):
    """Return mocked 'qip.copy_to_destination' function"""
    return mocker.patch.object(qip, "copy_to_destination")


@pytest.fixture()
def mocked_fetch_environ(mocker):
    """Return mocked 'qip.fetch_environ' function"""
    return mocker.patch.object(qip, "fetch_environ")


@pytest.fixture()
def mocked_filesystem_ensure_directory(mocker):
    """Return mocked 'qip.filesystem.ensure_directory' function"""
    return mocker.patch.object(qip.filesystem, "ensure_directory")


@pytest.fixture()
def mocked_filesystem_remove_directory_content(mocker):
    """Return mocked 'qip.filesystem.remove_directory_content' function"""
    return mocker.patch.object(qip.filesystem, "remove_directory_content")


@pytest.fixture()
def mocked_package_install(mocker):
    """Return mocked 'qip.package.install' function"""
    return mocker.patch.object(qip.package, "install")


@pytest.fixture()
def mocked_definition_create(mocker):
    """Return mocked 'qip.definition.create' function"""
    return mocker.patch.object(qip.definition, "create")


@pytest.fixture()
def mocked_definition_retrieve(mocker):
    """Return mocked 'qip.definition.retrieve' function"""
    return mocker.patch.object(qip.definition, "retrieve")


@pytest.fixture()
def mocked_wiz_export_definition(mocker):
    """Return mocked 'wiz.export_definition' function"""
    return mocker.patch.object(wiz, "export_definition")


@pytest.fixture()
def mocked_wiz_resolve_context(mocker):
    """Return mocked 'wiz.resolve_context' function"""
    return mocker.patch.object(wiz, "resolve_context")


@pytest.mark.parametrize("options, overwrite_packages, editable_mode", [
    ({}, False, False),
    ({"overwrite_packages": True}, True, False),
    ({"editable_mode": True}, False, True),
], ids=[
    "no-options",
    "with-overwrite-packages",
    "with-editable-mode",
])
def test_install(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_environ, mocked_package_install, mocked_copy_to_destination,
    mocked_definition_retrieve, mocked_definition_create,
    mocked_wiz_export_definition, mocked_filesystem_remove_directory_content,
    mocked_shutil_rmtree, options, overwrite_packages, editable_mode
):
    """Install packages."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "requirements": [
                {
                    "identifier": "?",
                    "request": "bim >= 3, < 4",
                },
                {
                    "identifier": "?",
                    "request": "bar",
                }
            ]
        },
        {
            "identifier": "Bar-22.3",
            "requirements": [
                {
                    "identifier": "Foo-0.2.3",
                    "request": "foo >= 0.1.0, < 1",
                }
            ]
        },
        {
            "identifier": "Bim-3.2.1",
            "requirements": [
                {
                    "identifier": "?",
                    "request": "bar > 22",
                }
            ]
        },
        {
            "identifier": "Bar-22.3",
            "requirements": [
                {
                    "identifier": "Foo-0.2.3",
                    "request": "foo >= 0.1.0, < 1",
                }
            ]
        }
    ]

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_environ.return_value = "__ENVIRON__"
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.side_effect = [True, True, True]

    qip.install(["foo", "bar"], "/path/to/install", **options)

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 2
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call(
        "/tmp2/lib/python2.7/site-packages"
    )

    mocked_fetch_environ.assert_called_once_with(
        mapping={"PYTHONPATH": "/tmp2/lib/python2.7/site-packages"}
    )

    assert mocked_package_install.call_count == 4
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=editable_mode
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bim >= 3, < 4", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bar > 22", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )

    assert mocked_copy_to_destination.call_count == 3
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )
    mocked_copy_to_destination.assert_any_call(
        packages[1], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )
    mocked_copy_to_destination.assert_any_call(
        packages[2], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )

    mocked_definition_retrieve.assert_not_called()
    mocked_definition_create.assert_not_called()
    mocked_wiz_export_definition.assert_not_called()

    assert mocked_filesystem_remove_directory_content.call_count == 3
    mocked_filesystem_remove_directory_content.assert_any_call("/tmp2")

    assert mocked_shutil_rmtree.call_count == 2
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


@pytest.mark.parametrize("options, overwrite_packages, editable_mode", [
    ({}, False, False),
    ({"overwrite_packages": True}, True, False),
    ({"editable_mode": True}, False, True),
], ids=[
    "no-options",
    "with-overwrite-packages",
    "with-editable-mode",
])
def test_install_with_definition_path(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_environ, mocked_package_install, mocked_copy_to_destination,
    mocked_definition_retrieve, mocked_definition_create,
    mocked_wiz_export_definition, mocked_filesystem_remove_directory_content,
    mocked_shutil_rmtree, options, overwrite_packages, editable_mode
):
    """Install packages with Wiz definitions."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "requirements": [
                {
                    "identifier": "?",
                    "request": "bim >= 3, < 4",
                },
                {
                    "identifier": "?",
                    "request": "bar",
                }
            ]
        },
        {
            "identifier": "Bar-22.3",
            "requirements": [
                {
                    "identifier": "Foo-0.2.3",
                    "request": "foo >= 0.1.0, < 1",
                }
            ]
        },
        {
            "identifier": "Bim-3.2.1",
        }
    ]

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_environ.return_value = "__ENVIRON__"
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.side_effect = [True, True, True]
    mocked_definition_retrieve.side_effect = ["__DATA1__", None, None]
    mocked_definition_create.side_effect = ["__DATA2__", "__DATA3__"]

    qip.install(
        ["foo", "bar"], "/path/to/install",
        definition_path="/path/to/definitions",
        **options
    )

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 3
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/definitions")
    mocked_filesystem_ensure_directory.assert_any_call(
        "/tmp2/lib/python2.7/site-packages"
    )

    mocked_fetch_environ.assert_called_once_with(
        mapping={"PYTHONPATH": "/tmp2/lib/python2.7/site-packages"}
    )

    assert mocked_package_install.call_count == 3
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=editable_mode
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bim >= 3, < 4", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )

    assert mocked_copy_to_destination.call_count == 3
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )
    mocked_copy_to_destination.assert_any_call(
        packages[1], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )
    mocked_copy_to_destination.assert_any_call(
        packages[2], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )

    assert mocked_definition_retrieve.call_count == 3
    mocked_definition_retrieve.assert_any_call(packages[0], "/tmp2")
    mocked_definition_retrieve.assert_any_call(packages[1], "/tmp2")
    mocked_definition_retrieve.assert_any_call(packages[2], "/tmp2")

    assert mocked_definition_create.call_count == 2
    mocked_definition_create.assert_any_call(packages[1], "/path/to/install")
    mocked_definition_create.assert_any_call(packages[2], "/path/to/install")

    assert mocked_wiz_export_definition.call_count == 3
    mocked_wiz_export_definition.assert_any_call(
        "/path/to/definitions", "__DATA1__"
    )
    mocked_wiz_export_definition.assert_any_call(
        "/path/to/definitions", "__DATA2__"
    )
    mocked_wiz_export_definition.assert_any_call(
        "/path/to/definitions", "__DATA3__"
    )

    assert mocked_filesystem_remove_directory_content.call_count == 3
    mocked_filesystem_remove_directory_content.assert_any_call("/tmp2")

    assert mocked_shutil_rmtree.call_count == 2
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


@pytest.mark.parametrize("options, overwrite_packages, editable_mode", [
    ({}, False, False),
    ({"overwrite_packages": True}, True, False),
    ({"editable_mode": True}, False, True),
], ids=[
    "no-options",
    "with-overwrite-packages",
    "with-editable-mode",
])
def test_install_without_dependencies(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_environ, mocked_package_install, mocked_copy_to_destination,
    mocked_definition_retrieve, mocked_definition_create,
    mocked_wiz_export_definition, mocked_filesystem_remove_directory_content,
    mocked_shutil_rmtree, options, overwrite_packages, editable_mode
):
    """Install packages with dependencies."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "requirements": [
                {
                    "identifier": "?",
                    "request": "bim >= 3, < 4",
                },
                {
                    "identifier": "?",
                    "request": "bar",
                }
            ]
        },
        {
            "identifier": "Bar-22.3",
            "requirements": [
                {
                    "identifier": "Foo-0.2.3",
                    "request": "foo >= 0.1.0, < 1",
                }
            ]
        }
    ]

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_environ.return_value = "__ENVIRON__"
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.side_effect = [True, True]

    qip.install(
        ["foo", "bar"], "/path/to/install", no_dependencies=True, **options
    )

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 2
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call(
        "/tmp2/lib/python2.7/site-packages"
    )

    mocked_fetch_environ.assert_called_once_with(
        mapping={"PYTHONPATH": "/tmp2/lib/python2.7/site-packages"}
    )

    assert mocked_package_install.call_count == 2
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=editable_mode
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )

    assert mocked_copy_to_destination.call_count == 2
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )
    mocked_copy_to_destination.assert_any_call(
        packages[1], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )

    mocked_definition_retrieve.assert_not_called()
    mocked_definition_create.assert_not_called()
    mocked_wiz_export_definition.assert_not_called()

    assert mocked_filesystem_remove_directory_content.call_count == 2
    mocked_filesystem_remove_directory_content.assert_any_call("/tmp2")

    assert mocked_shutil_rmtree.call_count == 2
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


@pytest.mark.parametrize("options, overwrite_packages, editable_mode", [
    ({}, False, False),
    ({"overwrite_packages": True}, True, False),
    ({"editable_mode": True}, False, True),
], ids=[
    "no-options",
    "with-overwrite-packages",
    "with-editable-mode",
])
def test_install_with_package_skipped(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_environ, mocked_package_install, mocked_copy_to_destination,
    mocked_definition_retrieve, mocked_definition_create,
    mocked_wiz_export_definition, mocked_filesystem_remove_directory_content,
    mocked_shutil_rmtree, options, overwrite_packages, editable_mode
):
    """Install packages with one package copy skipped."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "requirements": [
                {
                    "identifier": "?",
                    "request": "bim >= 3, < 4",
                },
                {
                    "identifier": "?",
                    "request": "bar",
                }
            ]
        }
    ]

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_environ.return_value = "__ENVIRON__"
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.return_value = False

    qip.install(["foo"], "/path/to/install", **options)

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 2
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call(
        "/tmp2/lib/python2.7/site-packages"
    )

    mocked_fetch_environ.assert_called_once_with(
        mapping={"PYTHONPATH": "/tmp2/lib/python2.7/site-packages"}
    )

    assert mocked_package_install.call_count == 1
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=editable_mode
    )

    assert mocked_copy_to_destination.call_count == 1
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite_packages=overwrite_packages
    )

    mocked_definition_retrieve.assert_not_called()
    mocked_definition_create.assert_not_called()
    mocked_wiz_export_definition.assert_not_called()
    mocked_filesystem_remove_directory_content.assert_not_called()

    assert mocked_shutil_rmtree.call_count == 2
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


def test_install_with_package_installation_error(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_environ, mocked_package_install, mocked_copy_to_destination,
    mocked_definition_retrieve, mocked_definition_create,
    mocked_wiz_export_definition, mocked_filesystem_remove_directory_content,
    mocked_shutil_rmtree, logger
):
    """Install packages with one package error which is skipped."""
    package = {"identifier": "Foo-0.2.3"}

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_environ.return_value = "__ENVIRON__"
    mocked_package_install.side_effect = [RuntimeError("Oops"), package]

    mocked_copy_to_destination.return_value = True

    qip.install(["foo", "bar"], "/path/to/install")

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 2
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call(
        "/tmp2/lib/python2.7/site-packages"
    )

    mocked_fetch_environ.assert_called_once_with(
        mapping={"PYTHONPATH": "/tmp2/lib/python2.7/site-packages"}
    )

    assert mocked_package_install.call_count == 2
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", "__ENVIRON__", "/tmp1",
        editable_mode=False
    )

    mocked_copy_to_destination.assert_called_once_with(
        package, "/tmp2", "/path/to/install", overwrite_packages=False
    )

    mocked_definition_retrieve.assert_not_called()
    mocked_definition_create.assert_not_called()
    mocked_wiz_export_definition.assert_not_called()

    assert mocked_filesystem_remove_directory_content.call_count == 1
    mocked_filesystem_remove_directory_content.assert_any_call("/tmp2")

    assert mocked_shutil_rmtree.call_count == 2
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.error.assert_called_once_with("Oops")


def test_copy_to_destination(
    mocked_click_confirm, mocked_shutil_rmtree, mocked_shutil_copytree,
    mocked_filesystem_ensure_directory, logger
):
    """Copy package to destination."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", "/path/to/destination"
    )
    assert result is True

    mocked_click_confirm.assert_not_called()
    mocked_shutil_rmtree.assert_not_called()

    mocked_shutil_copytree.assert_called_once_with(
        "/path/to/installed/package",
        "/path/to/destination/Foo/Foo-0.2.3"
    )

    mocked_filesystem_ensure_directory.assert_called_once_with(
        "/path/to/destination/Foo"
    )

    logger.warning.assert_not_called()
    logger.info.assert_called_once_with("Installed 'Foo-0.2.3'.")


def test_copy_to_destination_with_system_restriction(
    mocked_click_confirm, mocked_shutil_rmtree, mocked_shutil_copytree,
    mocked_filesystem_ensure_directory, logger
):
    """Copy package with system restriction to destination."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "system": {
            "os": {
                "name": "centos",
                "major_version": 7
            }
        }
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", "/path/to/destination"
    )
    assert result is True

    mocked_click_confirm.assert_not_called()
    mocked_shutil_rmtree.assert_not_called()

    mocked_shutil_copytree.assert_called_once_with(
        "/path/to/installed/package",
        "/path/to/destination/Foo/Foo-0.2.3-centos7"
    )

    mocked_filesystem_ensure_directory.assert_called_once_with(
        "/path/to/destination/Foo"
    )

    logger.warning.assert_not_called()
    logger.info.assert_called_once_with("Installed 'Foo-0.2.3-centos7'.")


def test_copy_to_destination_skip_existing(
    temporary_directory, mocked_click_confirm, mocked_shutil_rmtree,
    mocked_shutil_copytree, mocked_filesystem_ensure_directory, logger
):
    """Copy package to destination by skipping existing package."""
    path = os.path.join(temporary_directory, "Foo", "Foo-0.2.3")
    os.makedirs(path)

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", temporary_directory
    )
    assert result is False

    mocked_click_confirm.assert_not_called()
    mocked_shutil_rmtree.assert_not_called()

    mocked_shutil_copytree.assert_not_called()
    mocked_filesystem_ensure_directory.assert_not_called()

    logger.warning.assert_called_once_with(
        "Skip 'Foo-0.2.3' which is already installed."
    )
    logger.info.assert_not_called()


def test_copy_to_destination_overwrite_existing(
    temporary_directory, mocked_click_confirm, mocked_shutil_rmtree,
    mocked_shutil_copytree, mocked_filesystem_ensure_directory, logger
):
    """Copy package to destination by overwriting existing package."""
    path = os.path.join(temporary_directory, "Foo", "Foo-0.2.3")
    os.makedirs(path)

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", temporary_directory,
        overwrite_packages=True
    )
    assert result is True

    mocked_click_confirm.assert_not_called()

    mocked_shutil_rmtree.assert_called_once_with(path)

    mocked_shutil_copytree.assert_called_once_with(
        "/path/to/installed/package", path
    )

    mocked_filesystem_ensure_directory.assert_called_once_with(
        os.path.join(temporary_directory, "Foo")
    )

    logger.warning.assert_called_once_with(
        "Overwrite 'Foo-0.2.3' which is already installed."
    )
    logger.info.assert_called_once_with("Installed 'Foo-0.2.3'.")


def test_copy_to_destination_confirm_overwrite(
    temporary_directory, mocked_click_confirm, mocked_shutil_rmtree,
    mocked_shutil_copytree, mocked_filesystem_ensure_directory, logger
):
    """Ask user to confirm overwrite existing package."""
    path = os.path.join(temporary_directory, "Foo", "Foo-0.2.3")
    os.makedirs(path)

    # User answered No.
    mocked_click_confirm.return_value = False

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", temporary_directory,
        overwrite_packages=None
    )
    assert result is False

    mocked_click_confirm.assert_called_once_with(
        "Overwrite 'Foo-0.2.3'?"
    )
    mocked_shutil_rmtree.assert_not_called()

    mocked_shutil_copytree.assert_not_called()
    mocked_filesystem_ensure_directory.assert_not_called()

    logger.warning.assert_called_once_with(
        "Skip 'Foo-0.2.3' which is already installed."
    )
    logger.info.assert_not_called()


def test_fetch_environ(mocked_wiz_resolve_context):
    """Fetch and return environment mapping."""
    mocked_wiz_resolve_context.return_value = {"environ": "__ENVIRON__"}

    environ = qip.fetch_environ()
    assert environ == "__ENVIRON__"

    mocked_wiz_resolve_context.assert_called_once_with(
        ["python==2.7.*"], environ_mapping={}
    )


def test_fetch_environ_with_mapping(mocked_wiz_resolve_context):
    """Fetch and return environment mapping with initial mapping."""
    mocked_wiz_resolve_context.return_value = {"environ": "__ENVIRON__"}

    environ = qip.fetch_environ(mapping="__INITIAL_MAPPING__")
    assert environ == "__ENVIRON__"

    mocked_wiz_resolve_context.assert_called_once_with(
        ["python==2.7.*"], environ_mapping="__INITIAL_MAPPING__"
    )
