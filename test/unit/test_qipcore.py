# :coding: utf-8

from qip.qipcore import Qip, has_git_version
import os

class Logger(object):
    def debug(self, msg, **kwargs):
        print msg
    def warning(self, msg, **kwargs):
        print msg
    def error(self, msg, **kwargs):
        print msg
    def info(self, msg, **kwargs):
        print msg


TEST = {
    "server": "localhost",
    "platform": "el7-x86-64",
    "pipcmd": "/mill3d/server/apps/PYTHON/el7-x86-64/mill_python-2.7.12/bin/pip",
    "install_dir": "/tmp/packages/",
    "package_idx": "/tmp/index/"
}


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

def test_install_package():
    qip = Qip(TEST, "", Logger())
    qip.download_package('flask', '==1.0.2')
    qip.install_package("flask", '==1.0.2', True)
    assert os.path.exists('/tmp/packages/flask-1.0.2')
