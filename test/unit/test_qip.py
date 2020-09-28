# :coding: utf-8

import os
import sys
import shutil
import tempfile

import click
import pytest
import wiz
import wiz.filesystem

import qip
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
def mocked_click_prompt(mocker):
    """Return mocked 'click.prompt' function"""
    return mocker.patch.object(click, "prompt")


@pytest.fixture()
def mocked_confirm_overwrite(mocker):
    """Return mocked 'qip._confirm_overwrite' function"""
    return mocker.patch.object(qip, "_confirm_overwrite")


@pytest.fixture()
def mocked_install(mocker):
    """Return mocked 'qip._confirm_overwrite' function"""
    return mocker.patch.object(qip, "_install")


@pytest.fixture()
def mocked_copy_to_destination(mocker):
    """Return mocked 'qip.copy_to_destination' function"""
    return mocker.patch.object(qip, "copy_to_destination")


@pytest.fixture()
def mocked_fetch_context_mapping(mocker):
    """Return mocked 'qip.fetch_context_mapping' function"""
    return mocker.patch.object(qip, "fetch_context_mapping")


@pytest.fixture()
def mocked_fetch_definition_mapping(mocker):
    """Return mocked 'wiz.fetch_definition_mapping' function"""
    return mocker.patch.object(wiz, "fetch_definition_mapping")


@pytest.fixture()
def mocked_filesystem_ensure_directory(mocker):
    """Return mocked 'wiz.filesystem.ensure_directory' function"""
    return mocker.patch.object(wiz.filesystem, "ensure_directory")


@pytest.fixture()
def mocked_package_install(mocker):
    """Return mocked 'qip.package.install' function"""
    return mocker.patch.object(qip.package, "install")


@pytest.fixture()
def mocked_definition_export(mocker):
    """Return mocked 'qip.definition.export' function"""
    return mocker.patch.object(qip.definition, "export")


@pytest.fixture()
def mocked_definition_fetch_existing(mocker):
    """Return mocked 'qip.definition.fetch_existing' function"""
    return mocker.patch.object(qip.definition, "fetch_existing")


@pytest.fixture()
def mocked_definition_fetch_custom(mocker):
    """Return mocked 'qip.definition.fetch_custom' function"""
    return mocker.patch.object(qip.definition, "fetch_custom")


@pytest.fixture()
def mocked_fetch_environ(mocker):
    """Return mocked 'qip.environ.fetch' function"""
    return mocker.patch.object(qip.environ, "fetch")


@pytest.fixture()
def mocked_fetch_python_mapping(mocker):
    """Return mocked 'qip.environ.fetch_python_mapping' function"""
    return mocker.patch.object(qip.environ, "fetch_python_mapping")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target, registry_paths, "
    "update_existing_definitions, continue_on_error", [
        ({}, False, False, sys.executable, [], False, False),
        ({"overwrite": True}, True, False, sys.executable, [], False, False),
        (
            {"editable_mode": True}, False, True, sys.executable, [], False,
            False
        ),
        (
            {"python_target": "/bin/python3"}, False, False, "/bin/python3", [],
            False, False
        ),
        (
            {"registry_paths": ["/registry1", "registry2"]}, False, False,
            sys.executable, ["/registry1", "registry2"], False, False
        ),
        (
            {"update_existing_definitions": True}, False, False, sys.executable,
            [], True, False
        ),
        (
            {"continue_on_error": True}, False, False, sys.executable,
            [], False, True
        ),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
        "with-registries",
        "with-update-existing-definitions",
        "with-continue-on-error",
    ]
)
def test_install_requests(
    mocker, mocked_filesystem_ensure_directory, mocked_fetch_definition_mapping,
    mocked_tempfile_mkdtemp, mocked_fetch_context_mapping, mocked_install,
    mocked_shutil_rmtree, logger, options, overwrite, editable_mode,
    python_target, registry_paths, update_existing_definitions,
    continue_on_error
):
    """Install packages."""
    context = {"environ": {"PYTHONPATH": "/path/to/site-packages"}}
    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    mocked_install.side_effect = [
        ({"identifier": "foo", "requirements": ["bim"]}, overwrite),
        ({"identifier": "bar", "requirements": ["foo"]}, overwrite),
        ({"identifier": "bim"}, overwrite)
    ]

    result = qip.install(["foo", "bar"], "/path/to/install", **options)
    assert result is True

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 7
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_definition_mapping.assert_called_once_with(registry_paths)

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_install.call_count == 3
    mocked_install.assert_any_call(
        "foo", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bar", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bim", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=False,
        parent_identifier="foo",
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )

    assert mocked_shutil_rmtree.call_count == 5
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.info.assert_called_once_with("Packages installed: bar, bim, foo")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target, registry_paths, "
    "update_existing_definitions, continue_on_error", [
        ({}, False, False, sys.executable, [], False, False),
        ({"overwrite": True}, True, False, sys.executable, [], False, False),
        (
            {"editable_mode": True}, False, True, sys.executable, [], False,
            False
        ),
        (
            {"python_target": "/bin/python3"}, False, False, "/bin/python3", [],
            False, False
        ),
        (
            {"registry_paths": ["/registry1", "registry2"]}, False, False,
            sys.executable, ["/registry1", "registry2"], False, False
        ),
        (
            {"update_existing_definitions": True}, False, False, sys.executable,
            [], True, False
        ),
        (
            {"continue_on_error": True}, False, False, sys.executable,
            [], False, True
        ),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
        "with-registries",
        "with-update-existing-definitions",
        "with-continue-on-error",
    ]
)
def test_install_requests_with_definition_path(
    mocker, mocked_filesystem_ensure_directory, mocked_fetch_definition_mapping,
    mocked_tempfile_mkdtemp, mocked_fetch_context_mapping, mocked_install,
    mocked_shutil_rmtree, logger, options, overwrite, editable_mode,
    python_target, registry_paths, update_existing_definitions,
    continue_on_error
):
    """Install packages and export Wiz definitions."""
    context = {"environ": {"PYTHONPATH": "/path/to/site-packages"}}
    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    mocked_install.side_effect = [
        ({"identifier": "foo", "requirements": ["bim"]}, overwrite),
        ({"identifier": "bar", "requirements": ["foo"]}, overwrite),
        ({"identifier": "bim"}, overwrite)
    ]

    result = qip.install(
        ["foo", "bar"], "/path/to/install",
        definition_path="/path/to/definitions",
        **options
    )
    assert result is True

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 8
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_definition_mapping.assert_called_once_with(registry_paths)

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_install.call_count == 3
    mocked_install.assert_any_call(
        "foo", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path="/path/to/definitions",
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bar", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path="/path/to/definitions",
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bim", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path="/path/to/definitions",
        overwrite=overwrite,
        editable_mode=False,
        parent_identifier="foo",
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )

    assert mocked_shutil_rmtree.call_count == 5
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.info.assert_called_once_with("Packages installed: bar, bim, foo")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target, registry_paths, "
    "update_existing_definitions, continue_on_error", [
        ({}, False, False, sys.executable, [], False, False),
        ({"overwrite": True}, True, False, sys.executable, [], False, False),
        (
            {"editable_mode": True}, False, True, sys.executable, [], False,
            False
        ),
        (
            {"python_target": "/bin/python3"}, False, False, "/bin/python3", [],
            False, False
        ),
        (
            {"registry_paths": ["/registry1", "registry2"]}, False, False,
            sys.executable, ["/registry1", "registry2"], False, False
        ),
        (
            {"update_existing_definitions": True}, False, False, sys.executable,
            [], True, False
        ),
        (
            {"continue_on_error": True}, False, False, sys.executable,
            [], False, True
        ),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
        "with-registries",
        "with-update-existing-definitions",
        "with-continue-on-error",
    ]
)
def test_install_requests_without_dependencies(
    mocker, mocked_filesystem_ensure_directory, mocked_fetch_definition_mapping,
    mocked_tempfile_mkdtemp, mocked_fetch_context_mapping, mocked_install,
    mocked_shutil_rmtree, logger, options, overwrite, editable_mode,
    python_target, registry_paths, update_existing_definitions,
    continue_on_error
):
    """Install packages without dependencies."""
    context = {"environ": {"PYTHONPATH": "/path/to/site-packages"}}
    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    mocked_install.side_effect = [
        ({"identifier": "foo", "requirements": ["bim"]}, overwrite),
        ({"identifier": "bar", "requirements": ["foo"]}, overwrite)
    ]

    result = qip.install(
        ["foo", "bar"], "/path/to/install",
        no_dependencies=True,
        **options
    )
    assert result is True

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 5
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_definition_mapping.assert_called_once_with(registry_paths)

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_install.call_count == 2
    mocked_install.assert_any_call(
        "foo", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bar", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )

    assert mocked_shutil_rmtree.call_count == 4
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.info.assert_called_once_with("Packages installed: bar, foo")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target, registry_paths, "
    "update_existing_definitions, continue_on_error", [
        ({}, False, False, sys.executable, [], False, False),
        ({"overwrite": True}, True, False, sys.executable, [], False, False),
        (
            {"editable_mode": True}, False, True, sys.executable, [], False,
            False
        ),
        (
            {"python_target": "/bin/python3"}, False, False, "/bin/python3", [],
            False, False
        ),
        (
            {"registry_paths": ["/registry1", "registry2"]}, False, False,
            sys.executable, ["/registry1", "registry2"], False, False
        ),
        (
            {"update_existing_definitions": True}, False, False, sys.executable,
            [], True, False
        ),
        (
            {"continue_on_error": True}, False, False, sys.executable,
            [], False, True
        ),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
        "with-registries",
        "with-update-existing-definitions",
        "with-continue-on-error",
    ]
)
def test_install_requests_skip_installed(
    mocker, mocked_filesystem_ensure_directory, mocked_fetch_definition_mapping,
    mocked_tempfile_mkdtemp, mocked_fetch_context_mapping, mocked_install,
    mocked_shutil_rmtree, logger, options, overwrite, editable_mode,
    python_target, registry_paths, update_existing_definitions,
    continue_on_error
):
    """Skip package already installed during installation."""
    context = {"environ": {"PYTHONPATH": "/path/to/site-packages"}}
    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    mocked_install.side_effect = [
        (None, overwrite),
        ({"identifier": "bar"}, overwrite),
    ]

    result = qip.install(["foo", "bar"], "/path/to/install", **options)
    assert result is True

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 5
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_definition_mapping.assert_called_once_with(registry_paths)

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_install.call_count == 2
    mocked_install.assert_any_call(
        "foo", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bar", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )

    assert mocked_shutil_rmtree.call_count == 4
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.info.assert_called_once_with("Packages installed: bar")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target, registry_paths, "
    "update_existing_definitions, continue_on_error", [
        ({}, False, False, sys.executable, [], False, False),
        ({"overwrite": True}, True, False, sys.executable, [], False, False),
        (
            {"editable_mode": True}, False, True, sys.executable, [], False,
            False
        ),
        (
            {"python_target": "/bin/python3"}, False, False, "/bin/python3", [],
            False, False
        ),
        (
            {"registry_paths": ["/registry1", "registry2"]}, False, False,
            sys.executable, ["/registry1", "registry2"], False, False
        ),
        (
            {"update_existing_definitions": True}, False, False, sys.executable,
            [], True, False
        ),
        (
            {"continue_on_error": True}, False, False, sys.executable,
            [], False, True
        ),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
        "with-registries",
        "with-update-existing-definitions",
        "with-continue-on-error",
    ]
)
def test_install_requests_skip_existing(
    mocker, mocked_filesystem_ensure_directory, mocked_fetch_definition_mapping,
    mocked_tempfile_mkdtemp, mocked_fetch_context_mapping, mocked_install,
    mocked_shutil_rmtree, logger, options, overwrite, editable_mode,
    python_target, registry_paths, update_existing_definitions,
    continue_on_error
):
    """Skip package found in Wiz registries during installation."""
    context = {"environ": {"PYTHONPATH": "/path/to/site-packages"}}
    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    mocked_install.side_effect = [
        (
            {"identifier": "foo", "requirements": ["bim"], "skipped": True},
            overwrite
        ),
        ({"identifier": "bar"}, overwrite),
        ({"identifier": "bim"}, overwrite),
    ]

    result = qip.install(["foo", "bar"], "/path/to/install", **options)
    assert result is True

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 7
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_definition_mapping.assert_called_once_with(registry_paths)

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_install.call_count == 3
    mocked_install.assert_any_call(
        "foo", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bar", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bim", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=False,
        parent_identifier="foo",
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )

    assert mocked_shutil_rmtree.call_count == 5
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.info.assert_called_once_with("Packages installed: bar, bim")


@pytest.mark.parametrize(
    "options, editable_mode, python_target, registry_paths, "
    "update_existing_definitions, continue_on_error", [
        ({}, False, sys.executable, [], False, False),
        ({"editable_mode": True}, True, sys.executable, [], False, False),
        (
            {"python_target": "/bin/python3"}, False, "/bin/python3", [], False,
            False
        ),
        (
            {"registry_paths": ["/registry1", "registry2"]},
            False, sys.executable, ["/registry1", "registry2"], False, False
        ),
        (
            {"update_existing_definitions": True}, False, sys.executable,
            [], True, False
        ),
        (
            {"continue_on_error": True}, False, sys.executable,
            [], False, True
        ),
    ], ids=[
        "simple",
        "with-editable-mode",
        "with-python-target",
        "with-registries",
        "with-update-existing-definitions",
        "with-continue-on-error",
    ]
)
def test_install_requests_overwrite_changed(
    mocker, mocked_filesystem_ensure_directory, mocked_fetch_definition_mapping,
    mocked_tempfile_mkdtemp, mocked_fetch_context_mapping, mocked_install,
    mocked_shutil_rmtree, logger, options, editable_mode,
    python_target, registry_paths, update_existing_definitions,
    continue_on_error
):
    """Change value of overwrite during installation."""
    context = {"environ": {"PYTHONPATH": "/path/to/site-packages"}}
    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    mocked_install.side_effect = [
        ({"identifier": "foo"}, True),
        ({"identifier": "bar"}, True),
    ]

    result = qip.install(
        ["foo", "bar"], "/path/to/install", overwrite=None,
        **options
    )
    assert result is True

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 5
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_definition_mapping.assert_called_once_with(registry_paths)

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_install.call_count == 2
    mocked_install.assert_any_call(
        "foo", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=None,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )
    mocked_install.assert_any_call(
        "bar", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=True,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )

    assert mocked_shutil_rmtree.call_count == 4
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.info.assert_called_once_with("Packages installed: bar, foo")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target, registry_paths, "
    "update_existing_definitions, continue_on_error", [
        ({}, False, False, sys.executable, [], False, False),
        ({"overwrite": True}, True, False, sys.executable, [], False, False),
        (
            {"editable_mode": True}, False, True, sys.executable, [], False,
            False
        ),
        (
            {"python_target": "/bin/python3"}, False, False, "/bin/python3", [],
            False, False
        ),
        (
            {"registry_paths": ["/registry1", "registry2"]}, False, False,
            sys.executable, ["/registry1", "registry2"], False, False
        ),
        (
            {"update_existing_definitions": True}, False, False, sys.executable,
            [], True, False
        ),
        (
            {"continue_on_error": True}, False, False, sys.executable,
            [], False, True
        ),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
        "with-registries",
        "with-update-existing-definitions",
        "with-continue-on-error",
    ]
)
def test_install_requests_none(
    mocker, mocked_filesystem_ensure_directory, mocked_fetch_definition_mapping,
    mocked_tempfile_mkdtemp, mocked_fetch_context_mapping, mocked_install,
    mocked_shutil_rmtree, logger, options, overwrite, editable_mode,
    python_target, registry_paths, update_existing_definitions,
    continue_on_error
):
    """Install no packages."""
    context = {"environ": {"PYTHONPATH": "/path/to/site-packages"}}
    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_fetch_definition_mapping.return_value = "__MAPPING__"

    mocked_install.side_effect = [(None, overwrite)]

    result = qip.install(["foo"], "/path/to/install", **options)
    assert result is False

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 3
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_definition_mapping.assert_called_once_with(registry_paths)

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    mocked_install.assert_called_once_with(
        "foo", "/path/to/install", context, "__MAPPING__", "/tmp2", "/tmp1",
        mocker.ANY,
        definition_path=None,
        overwrite=overwrite,
        editable_mode=editable_mode,
        parent_identifier=None,
        update_existing_definitions=update_existing_definitions,
        continue_on_error=continue_on_error
    )

    assert mocked_shutil_rmtree.call_count == 3
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.info.assert_not_called()


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Install package."""
    installed_packages = set()

    mapping = {"identifier": "foo"}
    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_not_called()
    mocked_definition_fetch_existing.assert_not_called()
    mocked_definition_export.assert_not_called()

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_with_definition_path(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Install package and export Wiz definition."""
    installed_packages = set()

    mapping = {
        "identifier": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "3.8"
        }
    }

    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)
    mocked_definition_fetch_custom.return_value = None
    mocked_definition_fetch_existing.return_value = None

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_called_once_with(mapping)
    mocked_definition_fetch_existing.assert_called_once_with(
        mapping, "__MAPPING__", namespace=None
    )
    mocked_definition_export.assert_called_once_with(
        "/path/definitions", mapping, "/path/to/install",
        editable_mode=editable_mode,
        existing_definition=None,
        custom_definition=None
    )

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_with_custom_definition(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Install package and export Wiz definition from a custom definition."""
    installed_packages = set()

    custom_definition = wiz.definition.Definition({
        "identifier": "foo",
        "namespace": "test"
    })

    mapping = {
        "identifier": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "3.8"
        }
    }

    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)
    mocked_definition_fetch_custom.return_value = custom_definition
    mocked_definition_fetch_existing.return_value = None

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_called_once_with(mapping)
    mocked_definition_fetch_existing.assert_called_once_with(
        mapping, "__MAPPING__", namespace="test"
    )
    mocked_definition_export.assert_called_once_with(
        "/path/definitions", mapping, "/path/to/install",
        editable_mode=editable_mode,
        existing_definition=None,
        custom_definition=custom_definition
    )

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_with_existing_definition_in_output(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Install package and export Wiz definition from existing definition."""
    installed_packages = set()

    existing_definition = wiz.definition.Definition(
        {
            "identifier": "foo",
            "variants": [{"identifier": "3.8"}]
        },
        registry_path="/path/definitions"
    )

    mapping = {
        "identifier": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "3.8"
        }
    }

    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)
    mocked_definition_fetch_custom.return_value = None
    mocked_definition_fetch_existing.return_value = existing_definition

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        update_existing_definitions=True,
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_called_once_with(mapping)
    mocked_definition_fetch_existing.assert_called_once_with(
        mapping, "__MAPPING__", namespace=None
    )
    mocked_definition_export.assert_called_once_with(
        "/path/definitions", mapping, "/path/to/install",
        editable_mode=editable_mode,
        existing_definition=existing_definition,
        custom_definition=None
    )

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_with_existing_definition_with_different_variant(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Do not skip existing definition which does not have the same variant."""
    installed_packages = set()

    existing_definition = wiz.definition.Definition(
        {
            "identifier": "foo",
            "variants": [{"identifier": "V1"}]
        },
        registry_path="/somewhere/else"
    )

    mapping = {
        "identifier": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "3.8"
        }
    }

    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)
    mocked_definition_fetch_custom.return_value = None
    mocked_definition_fetch_existing.return_value = existing_definition

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        update_existing_definitions=True,
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_called_once_with(mapping)
    mocked_definition_fetch_existing.assert_called_once_with(
        mapping, "__MAPPING__", namespace=None
    )
    mocked_definition_export.assert_called_once_with(
        "/path/definitions", mapping, "/path/to/install",
        editable_mode=editable_mode,
        existing_definition=existing_definition,
        custom_definition=None
    )

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite", [
        ({}, False),
        ({"overwrite": True}, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
    ]
)
def test_install_one_request_with_existing_definition_in_editable_mode(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite,
):
    """Do not skip existing definition when editable mode is used."""
    installed_packages = set()

    existing_definition = wiz.definition.Definition(
        {
            "identifier": "foo",
            "variants": [{"identifier": "3.8"}]
        },
        registry_path="/somewhere/else"
    )

    mapping = {
        "identifier": "foo-0.1.0",
        "key": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "3.8"
        }
    }

    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)
    mocked_definition_fetch_custom.return_value = None
    mocked_definition_fetch_existing.return_value = existing_definition

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        editable_mode=True,
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=True
    )

    mocked_definition_fetch_custom.assert_called_once_with(mapping)
    mocked_definition_fetch_existing.assert_called_once_with(
        mapping, "__MAPPING__", namespace=None
    )

    mocked_definition_export.assert_called_once_with(
        "/path/definitions", mapping, "/path/to/install",
        editable_mode=True,
        existing_definition=None,
        custom_definition=None
    )

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite", [
        ({}, False),
        ({"overwrite": True}, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
    ]
)
def test_install_one_request_skip_existing_definition(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite,
):
    """Skip package because of existing definition."""
    installed_packages = set()

    existing_definition = wiz.definition.Definition(
        {
            "identifier": "foo",
            "variants": [{"identifier": "3.8"}]
        },
        registry_path="/somewhere/else"
    )

    mapping = {
        "identifier": "foo-0.1.0",
        "key": "foo",
        "version": "0.1.0",
        "python": {
            "identifier": "3.8"
        }
    }

    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)
    mocked_definition_fetch_custom.return_value = None
    mocked_definition_fetch_existing.return_value = existing_definition

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=False
    )

    mocked_definition_fetch_custom.assert_called_once_with(mapping)
    mocked_definition_fetch_existing.assert_called_once_with(
        mapping, "__MAPPING__", namespace=None
    )

    mocked_definition_export.assert_not_called()
    mocked_copy_to_destination.assert_not_called()

    logger.warning.assert_called_once_with(
        "Skip 'foo[3.8]==0.1.0' which already exists in Wiz registries."
    )
    logger.error.assert_not_called()
    logger.info.assert_not_called()

    assert mapping.get("skipped") is True


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_skip_installed(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Skip package if has already been installed."""
    installed_packages = {"foo-0.1.0"}

    mapping = {"identifier": "foo-0.1.0"}
    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)
    mocked_definition_fetch_custom.return_value = None
    mocked_definition_fetch_existing.return_value = None

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        **options
    )
    assert result == (None, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_not_called()
    mocked_definition_fetch_existing.assert_not_called()
    mocked_definition_export.assert_not_called()
    mocked_copy_to_destination.assert_not_called()
    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_not_called()

    assert mapping.get("skipped") is None


@pytest.mark.parametrize(
    "options, editable_mode", [
        ({}, False),
        ({"editable_mode": True}, True),
    ], ids=[
        "simple",
        "with-editable-mode",
    ]
)
def test_install_one_request_overwrite_changed(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, editable_mode,
):
    """Install package."""
    installed_packages = set()

    mapping = {"identifier": "foo-0.1.0"}
    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, True)

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        overwrite=None,
        **options
    )
    assert result == (mapping, True)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_not_called()
    mocked_definition_fetch_existing.assert_not_called()
    mocked_definition_export.assert_not_called()

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=None
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_copy_skipped(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Skip Wiz definition export is copy has been skipped."""
    installed_packages = set()

    mapping = {
        "identifier": "foo-0.1.0",
        "version": "0.1.0",
        "python": {
            "identifier": "3.8"
        }
    }

    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (True, overwrite)
    mocked_definition_fetch_custom.return_value = None
    mocked_definition_fetch_existing.return_value = None

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        definition_path="/path/definitions",
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_called_once_with(mapping)
    mocked_definition_fetch_existing.assert_called_once_with(
        mapping, "__MAPPING__", namespace=None
    )
    mocked_definition_export.assert_not_called()

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo'")

    assert mapping.get("skipped") is True


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_with_parent(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Install package with parent identifier."""
    installed_packages = set()

    mapping = {"identifier": "foo-0.1.0"}
    mocked_package_install.return_value = mapping
    mocked_copy_to_destination.return_value = (False, overwrite)

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        parent_identifier="bar",
        **options
    )
    assert result == (mapping, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode
    )

    mocked_definition_fetch_custom.assert_not_called()
    mocked_definition_fetch_existing.assert_not_called()
    mocked_definition_export.assert_not_called()

    mocked_copy_to_destination.assert_called_once_with(
        mapping, "/tmp/packages", "/path/to/install",
        overwrite=overwrite
    )

    logger.warning.assert_not_called()
    logger.error.assert_not_called()
    logger.info.assert_called_once_with("Requested 'foo' [from 'bar']")

    assert mapping.get("skipped") is False


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_fail(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Fail to install package."""
    installed_packages = set()

    mocked_package_install.side_effect = RuntimeError("Oh Shit")

    with pytest.raises(RuntimeError) as error:
        qip._install(
            "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
            "/tmp/packages", "/tmp/cache", installed_packages,
            **options
        )

    assert "Oh Shit" in str(error)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode,
    )

    mocked_definition_fetch_custom.assert_not_called()
    mocked_definition_fetch_existing.assert_not_called()
    mocked_definition_export.assert_not_called()
    mocked_copy_to_destination.assert_not_called()
    logger.warning.assert_not_called()
    logger.info.assert_not_called()
    logger.error.error()


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_continue_on_error(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Continue process when fail to install package."""
    installed_packages = set()

    mocked_package_install.side_effect = RuntimeError("Oh Shit")

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        continue_on_error=True,
        **options
    )
    assert result == (None, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode,
    )

    mocked_definition_fetch_custom.assert_not_called()
    mocked_definition_fetch_existing.assert_not_called()
    mocked_definition_export.assert_not_called()
    mocked_copy_to_destination.assert_not_called()
    logger.warning.assert_not_called()
    logger.info.assert_not_called()

    logger.error.assert_called_once_with("Request 'foo' has failed:\nOh Shit")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode", [
        ({}, False, False),
        ({"overwrite": True}, True, False),
        ({"editable_mode": True}, False, True),
    ], ids=[
        "simple",
        "with-overwrite-packages",
        "with-editable-mode",
    ]
)
def test_install_one_request_continue_on_error_with_parent(
    mocked_package_install, mocked_definition_fetch_custom,
    mocked_definition_fetch_existing, mocked_copy_to_destination,
    mocked_definition_export, logger, options, overwrite, editable_mode,
):
    """Continue process when fail to install package with parent identifier."""
    installed_packages = set()

    mocked_package_install.side_effect = RuntimeError("Oh Shit")

    result = qip._install(
        "foo", "/path/to/install", "__CONTEXT__", "__MAPPING__",
        "/tmp/packages", "/tmp/cache", installed_packages,
        parent_identifier="bar",
        continue_on_error=True,
        **options
    )
    assert result == (None, overwrite)

    mocked_package_install.assert_called_once_with(
        "foo", "/tmp/packages", "__CONTEXT__", "/tmp/cache",
        editable_mode=editable_mode,
    )

    mocked_definition_fetch_custom.assert_not_called()
    mocked_definition_fetch_existing.assert_not_called()
    mocked_definition_export.assert_not_called()
    mocked_copy_to_destination.assert_not_called()
    logger.warning.assert_not_called()
    logger.info.assert_not_called()

    logger.error.assert_called_once_with(
        "Request 'foo' has failed [from 'bar']:\nOh Shit"
    )


def test_copy_to_destination(
    mocked_click_prompt, mocked_shutil_rmtree, mocked_shutil_copytree,
    mocked_filesystem_ensure_directory, logger
):
    """Copy package to destination."""
    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "target": "Foo/Foo-0.2.3"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", "/path/to/destination"
    )
    assert result == (False, False)

    mocked_click_prompt.assert_not_called()
    mocked_shutil_rmtree.assert_not_called()

    mocked_shutil_copytree.assert_called_once_with(
        "/path/to/installed/package",
        "/path/to/destination/Foo/Foo-0.2.3"
    )

    mocked_filesystem_ensure_directory.assert_called_once_with(
        "/path/to/destination/Foo"
    )

    logger.warning.assert_not_called()
    logger.info.assert_called_once_with("\tInstalled 'Foo-0.2.3'.")


def test_copy_to_destination_with_system_restriction(
    mocked_click_prompt, mocked_shutil_rmtree, mocked_shutil_copytree,
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
        },
        "target": "Foo/Foo-0.2.3-centos7"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", "/path/to/destination"
    )
    assert result == (False, False)

    mocked_click_prompt.assert_not_called()
    mocked_shutil_rmtree.assert_not_called()

    mocked_shutil_copytree.assert_called_once_with(
        "/path/to/installed/package",
        "/path/to/destination/Foo/Foo-0.2.3-centos7"
    )

    mocked_filesystem_ensure_directory.assert_called_once_with(
        "/path/to/destination/Foo"
    )

    logger.warning.assert_not_called()
    logger.info.assert_called_once_with("\tInstalled 'Foo-0.2.3'.")


def test_copy_to_destination_skip_existing(
    temporary_directory, mocked_click_prompt, mocked_shutil_rmtree,
    mocked_shutil_copytree, mocked_filesystem_ensure_directory, logger
):
    """Copy package to destination by skipping existing package."""
    path = os.path.join(temporary_directory, "Foo", "Foo-0.2.3")
    os.makedirs(path)

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "target": "Foo/Foo-0.2.3"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", temporary_directory
    )
    assert result == (True, False)

    mocked_click_prompt.assert_not_called()
    mocked_shutil_rmtree.assert_not_called()

    mocked_shutil_copytree.assert_not_called()
    mocked_filesystem_ensure_directory.assert_not_called()

    logger.warning.assert_called_once_with(
        "Skip 'Foo-0.2.3' which is already installed."
    )
    logger.info.assert_not_called()


def test_copy_to_destination_overwrite_existing(
    temporary_directory, mocked_click_prompt, mocked_shutil_rmtree,
    mocked_shutil_copytree, mocked_filesystem_ensure_directory, logger
):
    """Copy package to destination by overwriting existing package."""
    path = os.path.join(temporary_directory, "Foo", "Foo-0.2.3")
    os.makedirs(path)

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "target": "Foo/Foo-0.2.3"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", temporary_directory,
        overwrite=True
    )
    assert result == (False, True)

    mocked_click_prompt.assert_not_called()

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
    logger.info.assert_called_once_with("\tInstalled 'Foo-0.2.3'.")


@pytest.mark.parametrize("overwrite, overwrite_next, expected", [
    (True, None, None),
    (False, None, None),
    (True, True, True),
    (False, False, False),
], ids=[
    "yes",
    "no",
    "yes-to-all",
    "no-to-all",
])
def test_copy_to_destination_confirm_overwrite(
    temporary_directory, mocked_confirm_overwrite, mocked_shutil_rmtree,
    mocked_shutil_copytree, mocked_filesystem_ensure_directory, logger,
    overwrite, overwrite_next, expected
):
    """Ask user to confirm overwrite existing package."""
    path = os.path.join(temporary_directory, "Foo", "Foo-0.2.3")
    os.makedirs(path)

    mocked_confirm_overwrite.return_value = (overwrite, overwrite_next)

    mapping = {
        "identifier": "Foo-0.2.3",
        "name": "Foo",
        "target": "Foo/Foo-0.2.3"
    }

    result = qip.copy_to_destination(
        mapping, "/path/to/installed/package", temporary_directory,
        overwrite=None
    )
    assert result == (not overwrite, expected)

    if overwrite:
        mocked_shutil_rmtree.assert_called_once()
        mocked_shutil_copytree.assert_called_once()
        mocked_filesystem_ensure_directory.assert_called_once()
        logger.warning.assert_called_once()

    else:
        mocked_shutil_rmtree.assert_not_called()
        mocked_shutil_copytree.assert_not_called()
        mocked_filesystem_ensure_directory.assert_not_called()

        logger.warning.assert_called_once_with(
            "Skip 'Foo-0.2.3' which is already installed."
        )
        logger.info.assert_not_called()


@pytest.mark.parametrize("answer, expected", [
    ("y", (True, None)),
    ("n", (False, None)),
    ("ya", (True, True)),
    ("na", (False, False)),
], ids=[
    "yes",
    "no",
    "yes-to-all",
    "no-to-all",
])
def test_confirm_overwrite(mocker, mocked_click_prompt, answer, expected):
    """Ask user to confirm overwrite existing package."""
    # User answered
    mocked_click_prompt.return_value = answer

    result = qip._confirm_overwrite("foo")

    assert result == expected
    mocked_click_prompt.assert_called_once_with(
        "Overwrite 'foo'? ([y]es, [n]o, [ya] yes to all, [na] no to all)",
        default='n',
        show_choices=False,
        show_default=False,
        type=mocker.ANY
    )


def test_fetch_context_mapping(
    mocked_fetch_environ, mocked_fetch_python_mapping
):
    """Return context mapping containing environment and python mapping."""
    mocked_fetch_environ.return_value = {
        "PATH": "/path/to/bin",
        "PYTHONPATH": "/path/to/lib",
    }
    mocked_fetch_python_mapping.return_value = {
        "library-path": "lib/python2.7/site-packages"
    }

    assert qip.fetch_context_mapping("/path", "python==2.7.*") == {
        "environ": {
            "PATH": "/path/to/bin",
            "PYTHONPATH": "/path/lib/python2.7/site-packages",
        },
        "python": {
            "library-path": "lib/python2.7/site-packages"
        }
    }
