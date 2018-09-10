# :coding: utf-8

import pytest
from qip.qipcore import Qip, has_git_version
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


def test_fetch_dependencies(logger, mocked_run_pip, mocker, tmpdir):
    """Fetch dependencies for requirement package."""
    mocked_run_pip = mocker.patch.object(Qip, "run_pip", autospec=True)
    mocked_run_pip.return_value = (
        "bar>=2.10\nbim==1.0\nbam>=0.14.1", "", 0
    )

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
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'foo'"
    )
    mocked_run_pip.assert_any_call(
        _qip,
        "download --exists-action w 'bar>=2.10' "
        "-d /tmp --no-binary :all: --no-cache"
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'bar>=2.10'"
    )
    mocked_run_pip.assert_any_call(
        _qip,
        "download --exists-action w 'bim==1.0' "
        "-d /tmp --no-binary :all: --no-cache"
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'bim==1.0'"
    )
    mocked_run_pip.assert_any_call(
        _qip,
        "download --exists-action w 'bam>=0.14.1' "
        "-d /tmp --no-binary :all: --no-cache"
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'bam>=0.14.1'"
    )
