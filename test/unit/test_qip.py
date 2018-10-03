# :coding: utf-8

import pytest
from mock import mock_open

import qip


def test_export_package_file(mocker):
    """Export a file listing the installed packages."""
    mocked_open = mock_open(mock=mocker.MagicMock())
    with mocker.patch('qip.open', mocked_open):
        qip.export_packages_file("/tmp", "")

    mocked_open.assert_called_once_with("/tmp/packages.txt", "w")
    mocked_open().write.assert_called_once_with("")
