# :coding: utf-8

import os
import sys
import shutil
import tempfile

import click
import pytest
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
def mocked_copy_to_destination(mocker):
    """Return mocked 'qip.copy_to_destination' function"""
    return mocker.patch.object(qip, "copy_to_destination")


@pytest.fixture()
def mocked_fetch_context_mapping(mocker):
    """Return mocked 'qip.fetch_context_mapping' function"""
    return mocker.patch.object(qip, "fetch_context_mapping")


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
def mocked_fetch_environ(mocker):
    """Return mocked 'qip.environ.fetch' function"""
    return mocker.patch.object(qip.environ, "fetch")


@pytest.fixture()
def mocked_fetch_python_mapping(mocker):
    """Return mocked 'qip.environ.fetch_python_mapping' function"""
    return mocker.patch.object(qip.environ, "fetch_python_mapping")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target", [
        ({}, False, False, sys.executable),
        ({"overwrite": True}, True, False, sys.executable),
        ({"editable_mode": True}, False, True, sys.executable),
        ({"python_target": "/bin/python3"}, False, False, "/bin/python3")
    ], ids=[
        "no-options",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
    ]
)
def test_install(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_context_mapping, mocked_package_install,
    mocked_copy_to_destination, mocked_definition_export,
    mocked_shutil_rmtree, options, overwrite, editable_mode, python_target
):
    """Install packages."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "name": "Foo",
            "version": "0.2.3",
            "requirements": [
                "bim >= 3, < 4",
                "bar",
            ]
        },
        {
            "identifier": "Bar-22.3",
            "name": "Bar",
            "version": "22.3",
            "requirements": [
                "foo",
            ]
        },
        {
            "identifier": "Bim-3.2.1",
            "name": "Bim",
            "version": "3.2.1",
            "requirements": [
                "bar > 22",
            ]
        },
        {
            "identifier": "Bar-22.3",
            "name": "Bar",
            "version": "22.3",
            "requirements": [
                "foo",
            ]
        }
    ]

    context = {
        "environ": {
            "PYTHONPATH": "/path/to/site-packages"
        }
    }

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.side_effect = [
        (True, overwrite), (True, overwrite), (True, overwrite)
    ]

    qip.install(["foo", "bar"], "/path/to/install", **options)

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 9
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_package_install.call_count == 4
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", context, "/tmp1",
        editable_mode=editable_mode
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", context, "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bim >= 3, < 4", "/tmp2", context, "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bar > 22", "/tmp2", context, "/tmp1",
        editable_mode=False
    )

    assert mocked_copy_to_destination.call_count == 3
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )
    mocked_copy_to_destination.assert_any_call(
        packages[1], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )
    mocked_copy_to_destination.assert_any_call(
        packages[2], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )

    mocked_definition_export.assert_not_called()

    assert mocked_shutil_rmtree.call_count == 6
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target, definition_mapping", [
        ({}, False, False, sys.executable, None),
        ({"overwrite": True}, True, False, sys.executable, None),
        ({"editable_mode": True}, False, True, sys.executable, None),
        ({"python_target": "/bin/python3"}, False, False, "/bin/python3", None),
        (
            {"definition_mapping": "__MAPPING__"},
            False, False, sys.executable, "__MAPPING__"
        ),
    ], ids=[
        "no-options",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
        "with-definition-mapping",
    ]
)
def test_install_with_definition_path(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_context_mapping, mocked_package_install,
    mocked_copy_to_destination, mocked_definition_export,
    mocked_shutil_rmtree, options, overwrite, editable_mode, python_target,
    definition_mapping
):
    """Install packages with Wiz definitions."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "requirements": [
                "bim >= 3, < 4",
                "bar",
            ]
        },
        {
            "identifier": "Bar-22.3",
            "requirements": [
                "foo",
            ]
        },
        {
            "identifier": "Bim-3.2.1",
        }
    ]

    context = {
        "environ": {
            "PYTHONPATH": "/path/to/site-packages"
        }
    }

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.side_effect = [
        (True, overwrite), (True, overwrite), (True, overwrite)
    ]

    qip.install(
        ["foo", "bar"], "/path/to/install",
        definition_path="/path/to/definitions",
        **options
    )

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 8
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/definitions")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_package_install.call_count == 3
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", context, "/tmp1",
        editable_mode=editable_mode
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", context, "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bim >= 3, < 4", "/tmp2", context, "/tmp1",
        editable_mode=False
    )

    assert mocked_copy_to_destination.call_count == 3
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )
    mocked_copy_to_destination.assert_any_call(
        packages[1], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )
    mocked_copy_to_destination.assert_any_call(
        packages[2], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )

    assert mocked_definition_export.call_count == 3
    mocked_definition_export.assert_any_call(
        "/path/to/definitions", packages[0], "/path/to/install",
        editable_mode=editable_mode,
        definition_mapping=definition_mapping
    )

    mocked_definition_export.assert_any_call(
        "/path/to/definitions", packages[1], "/path/to/install",
        editable_mode=False,
        definition_mapping=definition_mapping
    )
    mocked_definition_export.assert_any_call(
        "/path/to/definitions", packages[2], "/path/to/install",
        editable_mode=False,
        definition_mapping=definition_mapping
    )

    assert mocked_shutil_rmtree.call_count == 5
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target", [
        ({}, False, False, sys.executable),
        ({"overwrite": True}, True, False, sys.executable),
        ({"editable_mode": True}, False, True, sys.executable),
        ({"python_target": "/bin/python3"}, False, False, "/bin/python3")
    ], ids=[
        "no-options",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
    ]
)
def test_install_without_dependencies(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_context_mapping, mocked_package_install,
    mocked_copy_to_destination, mocked_definition_export,
    mocked_shutil_rmtree, options, overwrite, editable_mode, python_target
):
    """Install packages with dependencies."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "requirements": [
                "bim >= 3, < 4",
                "bar",
            ]
        },
        {
            "identifier": "Bar-22.3",
            "requirements": [
                "foo",
            ]
        }
    ]

    context = {
        "environ": {
            "PYTHONPATH": "/path/to/site-packages"
        }
    }

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.side_effect = [
        (True, overwrite), (True, overwrite)
    ]

    qip.install(
        ["foo", "bar"], "/path/to/install", no_dependencies=True, **options
    )

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 5
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_package_install.call_count == 2
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", context, "/tmp1",
        editable_mode=editable_mode
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", context, "/tmp1",
        editable_mode=False
    )

    assert mocked_copy_to_destination.call_count == 2
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )
    mocked_copy_to_destination.assert_any_call(
        packages[1], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )

    mocked_definition_export.assert_not_called()

    assert mocked_shutil_rmtree.call_count == 4
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


@pytest.mark.parametrize(
    "options, overwrite, editable_mode, python_target", [
        ({}, False, False, sys.executable),
        ({"overwrite": True}, True, False, sys.executable),
        ({"editable_mode": True}, False, True, sys.executable),
        ({"python_target": "/bin/python3"}, False, False, "/bin/python3")
    ], ids=[
        "no-options",
        "with-overwrite-packages",
        "with-editable-mode",
        "with-python-target",
    ]
)
def test_install_with_package_skipped(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_context_mapping, mocked_package_install,
    mocked_copy_to_destination, mocked_definition_export,
    mocked_shutil_rmtree, options, overwrite, editable_mode, python_target
):
    """Install packages with one package copy skipped."""
    packages = [
        {
            "identifier": "Foo-0.2.3",
            "requirements": [
                "bim >= 3, < 4",
                "bar",
            ]
        },
        {
            "identifier": "Bar-22.3",
            "requirements": [
                "foo",
            ]
        },
        {
            "identifier": "Bim-3.2.1",
        }
    ]

    context = {
        "environ": {
            "PYTHONPATH": "/path/to/site-packages"
        }
    }

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_package_install.side_effect = packages

    mocked_copy_to_destination.return_value = (False, overwrite)

    qip.install(["foo"], "/path/to/install", **options)

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 7
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_context_mapping.assert_called_once_with("/tmp2", python_target)

    assert mocked_package_install.call_count == 3
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", context, "/tmp1",
        editable_mode=editable_mode
    )

    assert mocked_copy_to_destination.call_count == 3
    mocked_copy_to_destination.assert_any_call(
        packages[0], "/tmp2", "/path/to/install",
        overwrite=overwrite
    )

    mocked_definition_export.assert_not_called()

    assert mocked_shutil_rmtree.call_count == 5
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")


def test_install_with_package_installation_error(
    mocked_filesystem_ensure_directory, mocked_tempfile_mkdtemp,
    mocked_fetch_context_mapping, mocked_package_install,
    mocked_copy_to_destination, mocked_definition_export,
    mocked_shutil_rmtree, logger
):
    """Install packages with one package error which is skipped."""
    package = {"identifier": "Foo-0.2.3"}

    context = {
        "environ": {
            "PYTHONPATH": "/path/to/site-packages"
        }
    }

    mocked_tempfile_mkdtemp.side_effect = ["/tmp1", "/tmp2"]
    mocked_fetch_context_mapping.return_value = context
    mocked_package_install.side_effect = [RuntimeError("Oops"), package]

    mocked_copy_to_destination.return_value = (True, True)

    qip.install(["foo", "bar"], "/path/to/install")

    assert mocked_tempfile_mkdtemp.call_count == 2

    assert mocked_filesystem_ensure_directory.call_count == 5
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/install")
    mocked_filesystem_ensure_directory.assert_any_call("/path/to/site-packages")
    mocked_filesystem_ensure_directory.assert_any_call("/tmp2")

    mocked_fetch_context_mapping.assert_called_once_with(
        "/tmp2", sys.executable
    )

    assert mocked_package_install.call_count == 2
    mocked_package_install.assert_any_call(
        "foo", "/tmp2", context, "/tmp1",
        editable_mode=False
    )
    mocked_package_install.assert_any_call(
        "bar", "/tmp2", context, "/tmp1",
        editable_mode=False
    )

    mocked_copy_to_destination.assert_called_once_with(
        package, "/tmp2", "/path/to/install", overwrite=False
    )

    mocked_definition_export.assert_not_called()

    assert mocked_shutil_rmtree.call_count == 4
    mocked_shutil_rmtree.assert_any_call("/tmp1")
    mocked_shutil_rmtree.assert_any_call("/tmp2")

    logger.error.assert_called_once_with("Request 'foo' has failed :\nOops")


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
    assert result == (True, False)

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
    assert result == (True, False)

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
    assert result == (False, False)

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
    assert result == (True, True)

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
    assert result == (overwrite, expected)

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
