# :coding: utf-8

from qip.qipcore import Qip, has_git_version
import os
import pytest

# Fake logger to remove mlog dependency for tests
class Logger(object):
    def debug(self, msg, **kwargs):
        print msg
    def warning(self, msg, **kwargs):
        print msg
    def error(self, msg, **kwargs):
        print msg
    def info(self, msg, **kwargs):
        print msg


# The test target is localhost with /tmp target folders
TEST = {
    "server": "localhost",
    "platform": "el7-x86-64",
    "pipcmd": "/mill3d/server/apps/PYTHON/el7-x86-64/mill_python-2.7.12/bin/pip",
    "install_dir": "/tmp/test-packages/",
    "package_idx": "/tmp/test-index/"
}


@pytest.fixture
def clear_directories():
    pass


def test_has_git_version():
    assert has_git_version("test.git") == False
    assert has_git_version("test.git@") == False
    assert has_git_version("test.git@1.90") == True
    assert has_git_version("test.git@master") == True


def test_get_name_and_specs_no_spec():
    qip = Qip(TEST, "", Logger())
    name, specs = qip.get_name_and_specs("flask")
    assert name == "flask"
    assert specs == [('==', '1.0.2')]


def test_get_name_and_specs_spec():
    qip = Qip(TEST, "", Logger())
    name, specs = qip.get_name_and_specs("flask==1.0.1")
    assert name == "flask"
    assert specs == [('==', '1.0.1')]
    name, specs = qip.get_name_and_specs("flask<1.0")
    assert name == "flask"
    assert specs == [('<', '1.0')]


def test_install_package(tmpdir):
    TEST['package_idx'] = str(tmpdir.mkdir("index"))
    TEST['install_dir'] = str(tmpdir.mkdir("packages"))
    qip = Qip(TEST, "", Logger())
    qip.download_package("flask", "==1.0.2")
    qip.install_package("flask", "==1.0.2", True)
    assert os.path.exists(TEST['install_dir'] + "/flask-1.0.2")
    assert os.path.exists(TEST['package_idx'] + \
                          "/Flask-1.0.2-py2.py3-none-any.whl")


def test_fetch_dependencies(tmpdir):
    TEST['package_idx'] = str(tmpdir.mkdir("index"))
    TEST['install_dir'] = str(tmpdir.mkdir("packages"))
    print TEST
    qip = Qip(TEST, "", Logger())
    deps = {}
    qip.fetch_dependencies("flask", deps)
    expected_deps = {u'MarkupSafe': [(u'>=', u'0.23')],
                     u'itsdangerous': [(u'>=', u'0.24')],
                     u'Jinja2': [(u'>=', u'2.10')],
                     u'click': [(u'>=', u'5.1')],
                     u'Werkzeug': [(u'>=', u'0.14')]}
    assert expected_deps == deps
