# :coding: utf-8

import os
import shutil
import tempfile
import uuid
import sys
import collections

import mlog
import pytest

import qip.symbol


@pytest.fixture()
def unique_name():
    """Return a unique name."""
    return "unique-{0}".format(uuid.uuid4())


@pytest.fixture()
def temporary_file(request):
    """Return a temporary file path."""
    file_handle, path = tempfile.mkstemp()
    os.close(file_handle)

    def cleanup():
        """Remove temporary file."""
        try:
            os.remove(path)
        except OSError:
            pass

    request.addfinalizer(cleanup)
    return path


@pytest.fixture()
def temporary_directory(request):
    """Return a temporary directory path."""
    path = tempfile.mkdtemp()

    def cleanup():
        """Remove temporary directory."""
        shutil.rmtree(path)

    request.addfinalizer(cleanup)

    return path


@pytest.fixture(autouse=True)
def mock_sys_version_info(mocker):
    """Mocked 'sys.version_info'."""
    _version = collections.namedtuple("version_info", "major, minor")
    mock = mocker.patch.object(sys, "version_info", _version(2, 8))
    reload(qip.symbol)
    return mock


@pytest.fixture()
def logger(mocker):
    """Mock the mlog module and return logger."""
    mocker.patch.object(mlog, "configure")
    mocker.patch.object(mlog, "root")

    mock_logger = mocker.Mock()
    mocker.patch.object(
        mlog, "Logger", return_value=mock_logger
    )
    return mock_logger
