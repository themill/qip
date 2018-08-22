# :coding: utf-8

from qip.qipcore import Qip, has_git_version
import os
import pytest
from unittest_helper import Logger, TEST


@pytest.fixture()
def dev_env(mocker):
    """Mock the environment variable used by config.

    Ensure that the environment variable CONFIG is explicitly set
    to config/base.py for the entirety of the module using the fixture.

    """
    mocker.patch.dict(os.environ, {
        "QIP_CONFIG": os.path.realpath(os.path.join(
            os.path.dirname(__file__), "../../source/qip/configs/testing.py"))
    })


def test_has_git_version():
    """
    Test the has_git_version function
    """
    assert has_git_version("test.git") is False
    assert has_git_version("test.git@") is False
    assert has_git_version("test.git@1.90") is True
    assert has_git_version("test.git@master") is True


def test_get_name_and_specs_no_spec(dev_env):
    """
    Check if the specs and name parsing works if no specs
    are supplied
    """
    qip = Qip(TEST, "", Logger())
    name, specs = qip.get_name_and_specs("flask")
    assert name == "flask"
    assert specs == [('==', '1.0.2')]


def test_get_name_and_specs_spec(dev_env):
    """
    Check that returned specs match if specs are supplied
    """
    qip = Qip(TEST, "", Logger())
    name, specs = qip.get_name_and_specs("flask==1.0.1")
    assert name == "flask"
    assert specs == [('==', '1.0.1')]
    name, specs = qip.get_name_and_specs("flask<1.0")
    assert name == "flask"
    assert specs == [('<', '1.0')]


def test_install_package(tmpdir, dev_env):
    """
    Test that packages are installed correctly
    """
    TEST['install_dir'] = str(tmpdir.mkdir("packages"))
    qip = Qip(TEST, "", Logger())
    qip.install_package("flask", "==1.0.2", True)
    assert os.path.exists(TEST['install_dir'] + "/flask-1.0.2")


def test_fetch_dependencies(tmpdir, dev_env):
    """
    Test that dependencies are resolved as expected.
    Dependencies for package should appear in the install
    dir
    """
    TEST['install_dir'] = str(tmpdir.mkdir("packages"))
    qip = Qip(TEST, "", Logger())
    deps = {}
    qip.fetch_dependencies("flask", deps)
    expected_deps = {u'MarkupSafe': [(u'>=', u'0.23')],
                     u'itsdangerous': [(u'>=', u'0.24')],
                     u'Jinja2': [(u'>=', u'2.10')],
                     u'click': [(u'>=', u'5.1')],
                     u'Werkzeug': [(u'>=', u'0.14')]}
    assert expected_deps == deps
