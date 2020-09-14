# :coding: utf-8

import subprocess

import pytest

import qip.command


@pytest.fixture()
def mocked_subprocess(mocker):
    """Return mocked subprocess."""
    _mocked_command = mocker.patch.object(subprocess, "Popen")
    return _mocked_command


@pytest.fixture()
def mocked_process(mocker):
    """Return mocked process."""
    return mocker.Mock()


def test_execute_verbose(mocked_subprocess, mocked_process, logger):
    """Execute a command verbose."""
    mocked_subprocess.return_value = mocked_process
    mocked_process.poll.side_effect = [None, None, None, False]
    mocked_process.stdout.readline.side_effect = [
        b"line one\n", b"line two\n", b"line three\n"
    ]
    mocked_process.stderr.readlines.return_value = []

    command = "pip install foo"
    output = qip.command.execute(command, {})

    assert logger.debug.call_count == 4
    logger.debug.assert_any_call("pip install foo")
    logger.debug.assert_any_call("line one")
    logger.debug.assert_any_call("line two")
    logger.debug.assert_any_call("line three")

    assert output == "line one\nline two\nline three\n"


def test_execute_quiet(mocked_subprocess, mocked_process, capsys):
    """Execute a command quiet."""
    mocked_subprocess.return_value = mocked_process
    mocked_process.communicate.return_value = (
        b"line one\nline two\nline three\n", b""
    )

    command = "pip install foo"
    output = qip.command.execute(command, {}, quiet=True)

    stdout_message, _ = capsys.readouterr()
    assert stdout_message == ""
    assert output == "line one\nline two\nline three\n"


def test_execute_stderr(mocked_subprocess, mocked_process):
    """Fail to execute a command."""
    mocked_subprocess.return_value = mocked_process
    mocked_process.communicate.return_value = (b"", b"stderr")
    command = "pip install foo"

    with pytest.raises(RuntimeError) as error:
        qip.command.execute(command, {}, quiet=True)
    assert str(error.value) == "stderr"
