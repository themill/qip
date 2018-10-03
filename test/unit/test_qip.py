# :coding: utf-8

import pytest
from mock import mock_open
import wiz

import qip


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


def test_export_package_definition(mocker):
    """Export Wiz definition for package."""
    mocked_export = mocker.patch.object(wiz, "export_definition")

    mapping = {
        "identifier": "Foo-0.1.0",
        "name": "Foo",
        "key": "foo",
        "version": "0.1.0",
        "description": "This is a Python package",
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": {
                "name": "centos",
                "major_version": 7
            }
        },
        "requirements": [
            {
                "identifier": "Bar-0.1.0",
                "request": "bar",
            },
            {
                "identifier": "Bim-2.3.1",
                "request": "bim >= 2, <3",
            }
        ]
    }
    expected = {
        "identifier": "foo",
        "version": "0.1.0",
        "description": "This is a Python package",
        "system": {
            "platform": "linux",
            "arch": "x86_64",
            "os": "centos >= 7, <8"
        },
        "requirements": [
            "bar",
            "bim >= 2, <3"
        ],
        "install-location": "/path"
    }

    qip.export_package_definition(mapping, "/path")

    mocked_export.assert_called_once_with("/path", expected)


def test_export_package_file(mocker):
    """Export a file listing the installed packages."""
    mocked_open = mock_open(mock=mocker.MagicMock())
    with mocker.patch('qip.open', mocked_open):
        qip.export_packages_file("/tmp", "")

    mocked_open.assert_called_once_with("/tmp/packages.txt", "w")
    mocked_open().write.assert_called_once_with("")


'''
from qip.core import Qip, has_git_version
import tempfile
import uuid


@pytest.fixture()
def mocked_run_pip(mocker):
    """Return mocked 'run_pip' command."""
    mocked_run_pip = mocker.patch.object(Qip, "run_pip", autospec=True)
    return mocked_run_pip


@pytest.fixture()
def mocked_uuid(mocker):
    """Return a predictable uuid for tmp directory"""
    mock_uuid = mocker.patch.object(uuid, 'uuid4', autospec=True)
    mock_uuid.return_value = uuid.UUID(hex='5ecd5827b6ef4067b5ac3ceac07dde9f')
    return mock_uuid


def test_has_git_version():
    """Check the git version from requirement."""
    assert has_git_version("test.git") is False
    assert has_git_version("test.git@") is False
    assert has_git_version("test.git@1.90") is True
    assert has_git_version("test.git@master") is True


def test_get_name_and_specs_no_spec(logger, mocked_run_pip, tmpdir):
    """Parse requirement with no specifier supplied.
    """
    mocked_run_pip.return_value = (
        "",
        (
            "Collecting foo==\n"
            "  Could not find a version that satisfies the requirement foo== "
            "(from versions: 0.1.0, 0.2.0, 0.3.0, 0.5.0)\n"
            "No matching distribution found for foo==\n"
        ),
        ""
    )

    _qip = Qip(tmpdir, logger)
    name, specs = _qip.get_name_and_specs("foo")
    mocked_run_pip.assert_called_once_with(
        _qip,
        "pip install --ignore-installed 'foo'=="
    )

    assert name == "foo"
    assert specs == [('==', '0.5.0')]


def test_get_name_and_specs_spec(logger, tmpdir):
    """Parse requirement with specifier supplied.
    """
    _qip = Qip(tmpdir, logger)
    name, specs = _qip.get_name_and_specs("foo==0.1.0")
    assert name == "foo"
    assert specs == [('==', '0.1.0')]

    name, specs = _qip.get_name_and_specs("foo<1.0")
    assert name == "foo"
    assert specs == [('<', '1.0')]


def test_install_package(logger, mocked_run_pip, mocked_uuid, mocker, tmpdir):
    """Install package in directory with correct version.
    """
    mkdtemp = mocker.patch.object(tempfile, 'mkdtemp')
    mkdtemp.return_value = "/tmp/testing"
    mocked_run_pip.return_value = (
        (
            "Installing collected packages: bar, bim, bam, foo\n"
            "Successfully installed bar-2.10 bim-1.0 bam-0.14.1 foo-0.1.0\n"
        ),
        "", 0
    )

    _qip = Qip('/tmp/testing', logger)
    _qip.install_package("foo", "==0.1.0", True)

    mocked_run_pip.assert_called_once_with(
        _qip,
        "install --ignore-installed --no-deps "
        "--prefix /tmp/tmp5ecd5827b6ef4067b5ac3ceac07dde9f"
        " --no-cache-dir  'foo==0.1.0'"
    )


deps = {"'foo'": (
                    "Collecting foo\n"
                    "Collecting bar>=2.10 (from foo)\n"
                    "Collecting bim==1.0 (from foo)\n"
                    "Collecting bam>=0.14.1 (from foo)", "", 0
               ),
        "'bar'": ("Collecting bar>=2.10 (from foo)\n", "", 0),
        "'bar>=2.10'": ("Collecting bar>=2.10 (from foo)\n", "", 0),
        "'bim'": ("Collecting bim==1.0 (from foo)\n", "", 0),
        "'bim==1.0'": ("Collecting bim==1.0 (from foo)\n", "", 0),
        "'bam'": ("Collecting bam>=0.14.1 (from foo))\n", "", 0),
        "'bam>=0.14.1'": ("Collecting bam>=0.14.1 (from foo))\n", "", 0),
        }


def dep_side_effect(package, *args, **kwargs):
    p = args[0].split()[3]
    print p, deps[p]
    return deps[p]


def test_fetch_dependencies(logger, mocked_run_pip, mocker, tmpdir):
    """Fetch dependencies for requirement package."""
    mocked_run_pip = mocker.patch.object(Qip, "run_pip", autospec=True)
    #mocked_run_pip.return_value = (
    #    "Collecting bar>=2.10 (from foo)\n"
    #    "Collecting bim==1.0 (from foo)\n"
    #    "Collecting bam>=0.14.1 (from foo)", "", 0
    #)
    mocked_run_pip.side_effect = dep_side_effect

    expected_deps = {}
    _qip = Qip(tmpdir, logger)
    _qip.fetch_dependencies("foo", expected_deps)

    assert expected_deps == {
        "bar": [(">=", "2.10")],
        "bim": [("==", "1.0")],
        "bam": [(">=", "0.14.1")],
    }

    assert mocked_run_pip.call_count == 4
    mocked_run_pip.assert_any_call(
        _qip,
        "download --exists-action w 'foo' "
        "-d /tmp --no-binary :all: --no-cache"

    )
    mocked_run_pip.assert_any_call(
        _qip,
        "download --exists-action w 'bar>=2.10' "
        "-d /tmp --no-binary :all: --no-cache"
    )
    mocked_run_pip.assert_any_call(
        _qip,
        "download --exists-action w 'bim==1.0' "
        "-d /tmp --no-binary :all: --no-cache"
    )
    mocked_run_pip.assert_any_call(
        _qip,
        "download --exists-action w 'bam>=0.14.1' "
        "-d /tmp --no-binary :all: --no-cache"
    )
'''