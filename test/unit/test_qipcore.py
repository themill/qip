# :coding: utf-8

from qip.qipcore import Qip, has_git_version
import os
from unittest_helper import Logger, TEST


def test_has_git_version():
    assert has_git_version("test.git") is False
    assert has_git_version("test.git@") is False
    assert has_git_version("test.git@1.90") is True
    assert has_git_version("test.git@master") is True


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
    qip.install_package("flask", "==1.0.2", True)
    assert os.path.exists(TEST['install_dir'] + "/flask-1.0.2")
    assert os.path.exists(TEST['package_idx'] +
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
