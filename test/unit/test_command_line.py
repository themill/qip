# :coding: utf-8

import os
import pytest

import qip
from qip.command_line import main


@pytest.fixture()
def set_development_environment_variable(mocker):
    """Mock the environment variable used by config.

    Ensure that the environment variable CONFIG is explicitly set
    to config/base.py for the entirety of the module using the fixture.

    """
    mocker.patch.dict(os.environ, {
        "QIP_CONFIG": os.path.realpath(os.path.join(
            os.path.dirname(__file__), "../../source/qip/config/base.py"))
    })


def test_without_arguments():
    """Command without arguments."""
    with pytest.raises(SystemExit) as raised:
        qip.command_line.main(arguments=None)

    assert raised.value.code == 0