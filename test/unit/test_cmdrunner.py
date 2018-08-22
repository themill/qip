# :coding: utf-8
from qip.cmdrunner import CmdRunner, LocalCmd
from unittest_helper import Logger, TEST
import os
import pytest


@pytest.fixture
def runner():
    return CmdRunner(TEST, "", Logger())


def test_mkdtemp(runner, tmpdir):
    """
    Test that the runner's mkdtemp creates
    temporary directory
    """
    tmp_path, _ = runner.mkdtemp(str(tmpdir))
    assert os.path.exists(tmp_path)


def test_install_and_sync_local(runner, tmpdir, monkeypatch):
    """
    Test the install and sync feature to ensure the rsync command
    generated is as expected
    """
    def mocked_runcmd(self, cmd):
        return cmd, "", 0
    monkeypatch.setattr(LocalCmd, 'run_cmd', mocked_runcmd)

    src_dir = str(tmpdir.mkdir("src"))
    assert os.path.exists(src_dir)
    cmd, _, _ = runner.install_and_sync(src_dir, str(tmpdir)+"/renamed")
    assert cmd == ("rsync -azvl {0}/ {1}"
                   .format(src_dir, str(tmpdir)+"/renamed"))


def test_install_and_sync_remote(runner, tmpdir, monkeypatch):
    pass


def test_rmtree(runner, tmpdir):
    """
    Test that the rmtree function of the runner
    deletes the directory tree
    """
    src_dir = str(tmpdir.mkdir("src"))
    assert os.path.exists(src_dir)
    runner.rmtree(str(tmpdir))
    assert os.path.exists(src_dir) is False
