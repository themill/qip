# :coding: utf-8

import os
import click
import shutil
import tempfile
import wiz

import pytest
from mock import mock_open

import qip


@pytest.mark.parametrize(
    "definition_exists",
[
    True, None
], ids=[
    "true",
    "false"
])
@pytest.mark.parametrize(
    "packages, mappings, installation_paths, expected",
[
    (
        ["foo"],
        [{
            "identifier": "Foo-0.1.0",
            "name": "Foo"
        }],
        ["/foo_path"],
        ["/foo_path"]
    ),
    (
        ["foo", "bar"],
        [{
            "identifier": "Foo-0.1.0",
            "name": "Foo"
        }, {
            "identifier": "Bar-2.3.0",
            "name": "Bar"
        }],
        ["/foo_path", "/bar_path"],
        ["/foo_path", "/bar_path"]
    ),
    (
        ["foo", "bar"],
        [{
            "identifier": "Foo-1.1.0",
            "name": "Foo"
        }, {

            "identifier": "bar-2.3.0",
            "name": "Bar",
            "requirements": [{
                "identifier": "Foo",
                "request": "foo >=1,<2"
            }]
        }, {
            "identifier": "Foo-1.1.0",
            "name": "Foo"
        }],
        ["/foo_path", "/bar_path", "/foo_path"],
        ["/foo_path", "/bar_path"]
    )
], ids=[
    "foo",
    "foo, bar",
    "foo recusive"
])
def test_install(
    mocker, packages, mappings, definition_exists, installation_paths, expected
):
    """Install packages to output_path from requests."""
    mocked_ensure_dir = mocker.patch.object(qip.filesystem, "ensure_directory")
    mocked_mkd = mocker.patch.object(tempfile, "mkdtemp", return_value="/tmp")
    mocked_fetch_environ = mocker.patch.object(qip, "fetch_environ")
    mocked_install = mocker.patch.object(qip.package, "install")
    mocked_install.side_effect = mappings
    mocked_copy = mocker.patch.object(qip, "copy_to_destination")
    mocked_copy.side_effect = installation_paths
    mocked_definition_retrieve = mocker.patch.object(
        qip.definition, "retrieve", return_value=definition_exists
    )
    mocked_definition_create = mocker.patch.object(qip.definition, "create")
    mocked_wiz_export = mocker.patch.object(wiz, "export_definition")
    mocked_rm = mocker.patch.object(qip.filesystem, "remove_directory_content")
    mocked_rm_tree = mocker.patch.object(shutil, "rmtree")

    output_path = "/path"
    qip.install(packages, output_path)

    mocked_ensure_dir.assert_called_once()
    mocked_mkd.assert_called_once()
    mocked_fetch_environ.assert_called_once_with(
        mapping={'PYTHONPATH': '/tmp/lib/python2.7/site-packages'}
    )
    mocked_install.assert_called()
    mocked_copy.assert_called()
    mocked_definition_retrieve.assert_called()
    if not definition_exists:
        mocked_definition_create.assert_called()
    mocked_wiz_export.assert_called()
    mocked_rm.assert_called_with("/tmp")
    mocked_rm_tree.assert_called_with("/tmp")


def test_install_fail(mocker):
    """Install packages fails on pip install."""
    mocker.patch.object(qip.filesystem, "ensure_directory")
    mocker.patch.object(tempfile, "mkdtemp", return_value="/tmp")
    mocker.patch.object(qip, "fetch_environ")
    mocked_install = mocker.patch.object(qip.package, "install")
    mocked_install.side_effect = RuntimeError()
    mocked_copy = mocker.patch.object(qip, "copy_to_destination")
    mocked_definition_create = mocker.patch.object(qip.definition, "create")
    mocked_definition_retrieve = mocker.patch.object(qip.definition, "retrieve")
    mocked_rm = mocker.patch.object(qip.filesystem, "remove_directory_content")
    mocked_rm_tree = mocker.patch.object(shutil, "rmtree")

    qip.install(["foo"], "/path")
    assert mocked_copy.call_count == 0
    assert mocked_definition_create.call_count == 0
    assert mocked_definition_retrieve.call_count == 0
    assert mocked_rm.call_count == 0
    mocked_rm_tree.assert_called_with("/tmp")


@pytest.mark.parametrize("overwrite", [
    True, False, None
], ids=[
    "true", "false", "none"
])
def test_copy_to_destination_overwrite(mocker, overwrite):
    """Overwrite during copy package."""
    mocker.patch.object(qip.filesystem, "ensure_directory")
    mocker.patch.object(shutil, "copytree")
    mocker.patch.object(os.path, "isdir", return_value=True)
    mocked_click = mocker.patch.object(click, "confirm")
    mocked_rm = mocker.patch.object(shutil, "rmtree")

    mapping = {
        "identifier": "Foo-0.1.0",
        "name": "Foo"
    }

    source = "/source"
    destination = "/destination"
    result = qip.copy_to_destination(mapping, source, destination, overwrite)

    if overwrite is None:
        mocked_click.assert_called_once()
    if overwrite:
        mocked_rm.assert_called_once_with("/destination/Foo/Foo-0.1.0")
        assert result == "/destination/Foo/Foo-0.1.0"
    if overwrite is False:
        assert result is None


@pytest.mark.parametrize("mapping, expected", [
    (
        {
            "identifier": "Foo-0.1.0",
            "name": "Foo"
        },
        "/destination/Foo/Foo-0.1.0"
    ),
    (
        {
            "identifier": "Foo-0.1.0",
            "name": "Foo",
            "system": {
                "os": {
                    "name": "centos",
                    "major_version": 7
                }
            }
        },
        "/destination/Foo/Foo-0.1.0-centos7"
    )
], ids=[
    "os-independent",
    "os-dependent"
])
def test_copy_to_destination(mocker, mapping, expected):
    """Copy package."""
    mocked_directory = mocker.patch.object(qip.filesystem, "ensure_directory")
    mocked_copy = mocker.patch.object(shutil, "copytree")

    source = "/source"
    destination = "/destination"
    result = qip.copy_to_destination(mapping, source, destination)

    mocked_directory.assert_called_once_with("/destination/Foo")
    mocked_copy.assert_called_once_with(
        "/source", expected
    )
    assert result == expected


@pytest.mark.parametrize("mapping, expected", [
    ({}, {}),
    (None, {})
], ids=[
    "mapping",
    "none"
])
def test_fetch_environ(mocker, mapping, expected):
    """Fetch mapping with all environment variables needed."""
    mocked_resolve = mocker.patch.object(
        wiz, "resolve_context", return_value={"environ": {}}
    )
    result = qip.fetch_environ(mapping)
    mocked_resolve.assert_called_once_with(
        ['python==2.7.*'], environ_mapping=expected
    )
    assert result == expected
