# :coding: utf-8
from qip.cmdrunner import CmdRunner
from unittest_helper import Logger, TEST
import os
import pytest


@pytest.fixture
def runner():
    return CmdRunner(TEST, "", Logger())


def test_mkdtemp(runner, tmpdir):
    tmp_path, _ = runner.mkdtemp(str(tmpdir))
    assert os.path.exists(tmp_path)


def test_rename_dir(runner, tmpdir):
    src_dir = str(tmpdir.mkdir("src"))
    assert os.path.exists(src_dir)
    runner.rename_dir(src_dir, str(tmpdir)+"/renamed")
    assert os.path.exists(str(tmpdir)+"/renamed")


def test_rmtree(runner, tmpdir):
    src_dir = str(tmpdir.mkdir("src"))
    assert os.path.exists(src_dir)
    runner.rmtree(str(tmpdir))
    assert os.path.exists(src_dir) is False
