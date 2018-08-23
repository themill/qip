# :coding: utf-8

import pytest

from qip.qipcore import Qip, has_git_version
import qip.cmdrunner


@pytest.fixture()
def mocked_cmd_runner(mocker):
    """Return mocked 'CmdRunner' instance."""
    instance = mocker.Mock()
    mocker.patch.object(qip.cmdrunner, "CmdRunner", return_value=instance)
    return instance


def test_has_git_version():
    """Check the git version from requirement."""
    assert has_git_version("test.git") is False
    assert has_git_version("test.git@") is False
    assert has_git_version("test.git@1.90") is True
    assert has_git_version("test.git@master") is True


def test_get_name_and_specs_no_spec(logger, mocked_cmd_runner):
    """Parse requirement with no specifier supplied.
    """
    mocked_cmd_runner.run_pip.return_value = (
        "",
        (
            "Collecting foo==\n"
            "  Could not find a version that satisfies the requirement foo== "
            "(from versions: 0.1.0, 0.2.0, 0.3.0, 0.5.0)\n"
            "No matching distribution found for foo==\n"
        ),
        ""
    )

    _qip = Qip({}, "P@$sw0rd", logger)
    name, specs = _qip.get_name_and_specs("foo")
    mocked_cmd_runner.run_pip.assert_called_once_with(
        "pip install --ignore-installed 'foo'=="
    )

    assert name == "foo"
    assert specs == [('==', '0.5.0')]


def test_get_name_and_specs_spec(logger, mocked_cmd_runner):
    """Parse requirement with specifier supplied.
    """
    _qip = Qip({}, "P@$sw0rd", logger)
    name, specs = _qip.get_name_and_specs("foo==0.1.0")
    assert name == "foo"
    assert specs == [('==', '0.1.0')]

    name, specs = _qip.get_name_and_specs("foo<1.0")
    assert name == "foo"
    assert specs == [('<', '1.0')]

    mocked_cmd_runner.assert_not_called()


def test_install_package(logger, mocked_cmd_runner):
    """Install package in directory with correct version.
    """
    mocked_cmd_runner.mkdtemp.return_value = ("/path/to/tmp", 0)
    mocked_cmd_runner.run_pip.return_value = (
        (
            "Installing collected packages: bar, bim, bam, foo\n"
            "Successfully installed bar-2.10 bim-1.0 bam-0.14.1 foo-0.1.0\n"
        ),
        "", 0
    )

    _qip = Qip({"install_dir": "/path/to/destination"}, "P@$sw0rd", logger)
    _qip.install_package("foo", "==0.1.0", True)

    mocked_cmd_runner.mkdtemp.assert_called_once_with("/tmp")
    mocked_cmd_runner.run_pip.assert_called_once_with(
        "pip install --ignore-installed --no-deps --prefix /path/to/tmp"
        " --no-cache-dir 'foo==0.1.0'"
    )
    mocked_cmd_runner.install_and_sync.assert_called_once_with(
        "/path/to/tmp", "/path/to/destination/foo-0.1.0"
    )
    mocked_cmd_runner.rmtree.assert_called_once_with("/path/to/tmp")


def test_fetch_dependencies(logger, mocked_cmd_runner):
    """Fetch dependencies for requirement package."""
    mocked_cmd_runner.run_pip.return_value = (
        "bar>=2.10\nbim==1.0\nbam>=0.14.1", "", 0
    )

    expected_deps = {}
    _qip = Qip({}, "P@$sw0rd", logger)
    _qip.fetch_dependencies("foo", expected_deps)

    assert expected_deps == {
        "bar": [(">=", "2.10")],
        "bim": [("==", "1.0")],
        "bam": [(">=", "0.14.1")],
    }

    assert mocked_cmd_runner.run_pip.call_count == 4
    mocked_cmd_runner.run_pip.assert_any_call(
        "pip download --exists-action w 'foo' "
        "-d /tmp --no-binary :all: --no-cache"
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'foo'"
    )
    mocked_cmd_runner.run_pip.assert_any_call(
        "pip download --exists-action w 'bar>=2.10' "
        "-d /tmp --no-binary :all: --no-cache"
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'bar>=2.10'"
    )
    mocked_cmd_runner.run_pip.assert_any_call(
        "pip download --exists-action w 'bim==1.0' "
        "-d /tmp --no-binary :all: --no-cache"
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'bim==1.0'"
    )
    mocked_cmd_runner.run_pip.assert_any_call(
        "pip download --exists-action w 'bam>=0.14.1' "
        "-d /tmp --no-binary :all: --no-cache"
        "| grep Collecting | cut -d' ' "
        "-f2 | grep -v 'bam>=0.14.1'"
    )
