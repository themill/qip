# :coding: utf-8

import os
import shutil
import tempfile
import uuid

import pytest


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
def logger(mocker):
    """Mock the 'qip.logging' module and return logger."""
    import qip.logging
    mocker.patch.object(qip.logging, "configure")
    mocker.patch.object(qip.logging, "root")

    mock_logger = mocker.Mock()
    mocker.patch.object(
        qip.logging, "Logger", return_value=mock_logger
    )
    return mock_logger
