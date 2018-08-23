# :coding: utf-8

import uuid

import wiz
import pytest

from qip.cmdrunner import LocalCmd


@pytest.fixture()
def mocked_uuid_v4(mocker):
    """return mocked 'uuid.uuid4' function."""
    return mocker.patch.object(
        uuid, "uuid4", return_value=mocker.Mock(hex="__UNIQUE__")
    )


@pytest.fixture()
def mocked_run_cmd(mocker):
    """Return mocked 'LocalCmd.run_cmd' function."""
    return mocker.patch.object(
        LocalCmd, "run_cmd", return_value=(
            "__stdout__", "__stderr__", "__returncode__"
        )
    )


@pytest.fixture()
def mocked_wiz_resolve_context(mocker):
    """Return mocked 'wiz.resolve_context' function."""
    return mocker.patch.object(
        wiz, "resolve_context", return_value={"environ": "__ENVIRON__"}
    )


@pytest.mark.usefixtures("mocked_uuid_v4")
def test_mkdtemp_default(logger, mocked_run_cmd):
    """Create temporary folder in path.
    """
    runner = LocalCmd({}, "P@$sw0rd", logger)
    tmp_path, exit_status = runner.mkdtemp("/path/to/tmp/")
    mocked_run_cmd.assert_called_once_with(
        "mkdir -m 755 /path/to/tmp/tmp__UNIQUE__"
    )
    assert tmp_path == "/path/to/tmp/tmp__UNIQUE__"
    assert exit_status == "__returncode__"


@pytest.mark.usefixtures("mocked_uuid_v4")
def test_mkdtemp(logger, mocked_run_cmd):
    """Create temporary folder in default path.
    """
    runner = LocalCmd({"install_dir": "/path/to/default"}, "P@$sw0rd", logger)
    tmp_path, exit_status = runner.mkdtemp()
    mocked_run_cmd.assert_called_once_with(
        "mkdir -m 755 /path/to/default/tmp__UNIQUE__"
    )
    assert tmp_path == "/path/to/default/tmp__UNIQUE__"
    assert exit_status == "__returncode__"


@pytest.mark.parametrize("destination, commands", [
    (
        "/mill3d/server/apps/THING/stuff",
        [
            "rsync -azvl /source/ master:/mill3d/server/apps/THING/stuff",
            "rsync -azvl /source/ marmont:/mill3d/server/apps/THING/stuff",
            "rsync -azvl /source/ bugsy:/mill3d/server/apps/THING/stuff",
            "rsync -azvl /source/ turing:/mill3d/server/apps/THING/stuff",
            "rsync -azvl /source/ cobra:/mill3d/server/apps/THING/stuff",
        ]
    ),
    (
        "/path/to/stuff",
        ["rsync -azvl /source/ /path/to/stuff"]
    ),
], ids=[
    "mill3d-source",
    "other-source"
])
def test_install_and_sync(logger, mocked_run_cmd, destination, commands):
    """Sync folder to a destination, on the mill3d server mount or not.
    """
    runner = LocalCmd({}, "P@$sw0rd", logger)
    stdout, stderr, exit_status = runner.install_and_sync(
        "/source", destination
    )

    assert mocked_run_cmd.call_count == len(commands)
    for command in commands:
        mocked_run_cmd.assert_any_call(command)

    assert stdout == "__stdout__"
    assert stderr == "__stderr__"
    assert exit_status == "__returncode__"


def test_install_and_sync_error(logger, mocked_run_cmd):
    """Report error when exit status of command does not return zero.
    """
    mocked_run_cmd.return_value = (
        "__stdout__", "Is Sven a reindeer or a moose in Frozen?", 2
    )

    runner = LocalCmd({}, "P@$sw0rd", logger)
    stdout, stderr, exit_status = runner.install_and_sync(
        "/source", "/mill3d/server/apps/THING/stuff"
    )

    assert stdout == "__stdout__"
    assert stderr == "Is Sven a reindeer or a moose in Frozen?"
    assert exit_status == 2

    assert logger.error.call_count == 5
    logger.error.assert_any_call(
        "Sync to 'master' failed with error: "
        "Is Sven a reindeer or a moose in Frozen?\n"
        "Carrying on with other servers."
    )
    logger.error.assert_any_call(
        "Sync to 'marmont' failed with error: "
        "Is Sven a reindeer or a moose in Frozen?\n"
        "Carrying on with other servers."
    )
    logger.error.assert_any_call(
        "Sync to 'bugsy' failed with error: "
        "Is Sven a reindeer or a moose in Frozen?\n"
        "Carrying on with other servers."
    )
    logger.error.assert_any_call(
        "Sync to 'turing' failed with error: "
        "Is Sven a reindeer or a moose in Frozen?\n"
        "Carrying on with other servers."
    )
    logger.error.assert_any_call(
        "Sync to 'cobra' failed with error: "
        "Is Sven a reindeer or a moose in Frozen?\n"
        "Carrying on with other servers."
    )


def test_rmtree(mocked_run_cmd, logger):
    """Remove folder."""
    runner = LocalCmd({}, "P@$sw0rd", logger)
    stdout, stderr, exit_status = runner.rmtree("/path/to/folder")
    mocked_run_cmd.assert_called_once_with("rm -rf /path/to/folder")

    assert stdout == "__stdout__"
    assert stderr == "__stderr__"
    assert exit_status == "__returncode__"


def test_run_pip(mocked_run_cmd, logger, mocked_wiz_resolve_context):
    """Run pip command."""
    runner = LocalCmd({}, "P@$sw0rd", logger)
    stdout, stderr, exit_status = runner.run_pip("install thing")
    mocked_run_cmd.assert_called_once_with("pip install thing", "__ENVIRON__")
    mocked_wiz_resolve_context.assert_called_once_with(["python==2.7.*"])

    assert stdout == "__stdout__"
    assert stderr == "__stderr__"
    assert exit_status == "__returncode__"
