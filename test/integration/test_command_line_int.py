# :coding: utf-8

import os
import pytest
import shutil
import getpass

from click.testing import CliRunner

from qip.command_line import qipcmd


@pytest.fixture()
def base_config(mocker):
    """Mock the environment variable used by config.

    Ensure that the environment variable CONFIG is explicitly set
    to config/base.py for the tests using the fixture.

    """
    mocker.patch.dict(os.environ, {
        "QIP_CONFIG": os.path.realpath(os.path.join(
            os.path.dirname(__file__), "../../source/qip/configs/base.py"))
    })


@pytest.fixture()
def testing_config(mocker, request):
    """Mock the environment variable used by config.

    Ensure that the environment variable CONFIG is explicitly set
    to config/testing.py for the tests using the fixture.

    """
    # TODO: instead of mocking the config, we should mock the calls retrieving
    # the paths and create one time directories. Otherwise we might delete
    # someones actual tests somewhere when running the tests.
    mocker.patch.dict(os.environ, {
        "QIP_CONFIG": os.path.realpath(os.path.join(
            os.path.dirname(__file__), "../../source/qip/configs/testing.py"))
    })

    def cleanup():
        """Remove temporary directory and reset environment."""
        # TODO: get paths from config or create new tmp paths instead of config
        paths = ["/tmp/index/", "/tmp/packages/"]
        for path in paths:
            if os.path.exists(path) and os.path.isdir(path):
                shutil.rmtree(path)

    request.addfinalizer(cleanup)


def test_without_arguments():
    """Command without arguments prints help."""
    runner = CliRunner()
    result_help = runner.invoke(qipcmd, ["--help"])
    result = runner.invoke(
        qipcmd, input='\ry\n'
    )
    assert result.exit_code == 0
    assert not result.exception
    assert result.output == result_help.output


@pytest.mark.usefixtures("base_config")
def test_target_prompt():
    """Prompt asks for User Password."""
    runner = CliRunner()
    result = runner.invoke(qipcmd, ['install', 'test'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.split('\n')[0] == "Targets:"


@pytest.mark.usefixtures("base_config")
def test_password_fail():
    """Prompt asks for User Password.
    This test will fail if there's an shh key on the target server
    """
    runner = CliRunner()
    result = runner.invoke(
        qipcmd, ['--target', 'centos72', 'install', 'test'], input='test\n'
    )

    assert not result.exit_code == 0
    assert result.exception
    assert (
        "error: Unable to connect to dev3d-3 as {}.".format(getpass.getuser())
        in result.output
    )


def test_install_no_user():
    """Install without a user directory in London.

    Using an LA test user, execute an install command and it should still
    install it to the target location.

    """
    pass


def test_sync():
    """Sync installed packages."""
    pass
