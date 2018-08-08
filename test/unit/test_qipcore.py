# :coding: utf-8

import os
import pytest

from qip.qipcore import *

def test_has_git_version():
    assert has_git_version("test.git") == False
    assert has_git_version("test.git@") == False
    assert has_git_version("test.git@1.90") == True
    assert has_git_version("test.git@master") == True