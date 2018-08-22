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
    result = runner.invoke(qipcmd, ['download', 'test'])

    assert not result.exit_code == 0
    assert result.exception
    assert result.output.split('\n')[0] == "Targets:"


@pytest.mark.usefixtures("base_config")
def test_password_fail():
    """Prompt asks for User Password."""
    runner = CliRunner()
    result = runner.invoke(
        qipcmd, ['--target', 'centos72', 'download', 'test'], input='test\n'
    )

    assert not result.exit_code == 0
    assert result.exception
    assert (
        "Error: Unable to connect to dev3d-3 as {}.".format(getpass.getuser())
        in result.output.split('\n')[-3]
    )


@pytest.mark.parametrize(
    "package, expected_output, expected_package",
    [
        (
            "flask==1.0.2",
            "Successfully installed flask-1.0.2",
            "flask-1.0.2"
        ),
        (
            "flask",
            "Successfully installed flask-1.0.2",
            "flask-1.0.2"
        )
    ],
    ids=[
        "install external package with version: flask",
        "install external package without version: flask",
    ]
)
@pytest.mark.usefixtures("testing_config")
def test_install_external(package, expected_output, expected_package):
    """Install external library.

    Using the test config:

    - execute for external packages
        qip --target test install {package}={version}

    The package should appear in /tmp/packages

    """
    runner = CliRunner()
    result = runner.invoke(
        qipcmd, ['--target', 'test', 'install', package],
        color=False, input='\ny\n'
    )
    assert result.exit_code == 0
    assert not result.exception
    # TODO: get paths from config or create new tmp paths instead of config
    assert expected_output in result.output.split('\n')[-2]
    assert os.path.exists('/tmp/packages')
    assert os.path.isdir('/tmp/packages')
    assert os.path.isdir('/tmp/packages/{}'.format(expected_package))



@pytest.mark.parametrize(
    "repo, package, expected_output, expected_package",
    [
        (
            "git@gitlab:rnd/mlog.git@0.2.1",
            "mlog==0.2.1",
            "Successfully installed mlog-0.2.1",
            "mlog-0.2.1.zip"
        ),
        (
            "git@gitlab:rnd/mlog.git@0.2.1",
            "mlog",
            "Successfully installed mlog-0.2.1",
            "mlog-0.2.1.zip"
        ),
    ],
    ids=[
        "install internal package with version: mlog",
        "install internal package without version: mlog",
    ]
)
@pytest.mark.usefixtures("testing_config")
def test_install_internal(repo, package, expected_output, expected_package):
    """Install internal library from gitlab.

    Using the test config:

    - execute for internal packages:
        qip --target test install {package}=={version}

    This will download the package first from the gitlab repo, and then install
    it into /tmp/packages.

    """
    runner = CliRunner()

    # download
    result = runner.invoke(
        qipcmd, ['--target', 'test', 'download', repo], color=False
    )
    assert result.exit_code == 0
    assert not result.exception

    # install
    result = runner.invoke(
        qipcmd, ['--target', 'test', 'install', package],
        color=False, input='\ny\n'
    )
    assert result.exit_code == 0
    assert not result.exception
    # TODO: get paths from config or create new tmp paths instead of config
    assert expected_output in result.output.split('\n')[-2]
    assert os.path.exists('/tmp/packages')
    assert os.path.isdir('/tmp/packages')
    assert os.path.isdir('/tmp/packages/{}'.format(expected_package))


def test_install_no_user():
    """Install without a user directory in London.

    Using an LA test user, execute an install command and it should still
    install it to the target location.

    """
    pass


def test_sync():
    """Sync installed packages."""
    pass
