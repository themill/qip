# :coding: utf-8

import json
import re
import os
import textwrap

import pytest
import wiz.utility

import qip.command
import qip.system
from qip.environ import PYTHON_INFO_SCRIPT
from qip.package import PACKAGE_INFO_SCRIPT

#: Context mapping mocked for Python 2.7
PYTHON_MAPPING_27 = {
    "identifier": "2.7",
    "library-path": "lib/python2.7/site-packages",
    "request": "python >= 2.7, < 2.8"
}

#: Collection of all packages dependency mapping available for testings.
PACKAGE_DEPENDENCY_MAPPING = {
    "foo": {
        "package": {
            "installed_version": "1.2.0",
            "key": "foo",
            "module_name": "foo_module",
            "package_name": "Foo"
        },
        "requirements": [
            "bim >= 3.4, < 5"
        ]
    },
    "bar": {
        "package": {
            "installed_version": "0.1.0",
            "key": "bar",
            "module_name": "bar_module",
            "package_name": "Bar"
        },
        "requirements": [
            "foo"
        ]
    },
    "bim": {
        "package": {
            "installed_version": "3.6.2",
            "key": "bim",
            "module_name": "bim_module",
            "package_name": "BIM"
        }
    },
}

#: Collection of metadata per package name.
METADATA_MAPPING = {
    "foo": textwrap.dedent(
        """
        Summary: Foo Python Package.
        Location: /path/to/foo
        Entry-points:
          [console_scripts]
          foo = foo.__main__:main
        """
    ),
    "bar": textwrap.dedent(
        """
        Summary: Bar Python Package.
        Location: /path/to/bar
        Classifiers:
          Operating System :: Unix
        """
    ),
    "bim": textwrap.dedent(
        """
        Summary: Bim Python Package.
        Location: /path/to/bim
        """
    ),
}


@pytest.fixture(autouse=True)
def mock_commands(mocker):
    """Mock all subprocesses used for installing a package with Python 2.7."""

    def _command_execute(command, *args, **kwargs):
        """Mock :func:`qip.command.execute` depending on context."""
        if command.startswith("python {}".format(PYTHON_INFO_SCRIPT)):
            return json.dumps(PYTHON_MAPPING_27)

        elif command.startswith("python -m pip install"):
            request = re.search(r"'(.+)'", command).group(1)
            output = re.search(r"--prefix ([^ ]+)", command).group(1)
            requirement = wiz.utility.get_requirement(request)
            os.makedirs(os.path.join(output, requirement.name))
            return "Installing collected packages: {}".format(requirement.name)

        elif command.startswith("python {}".format(PACKAGE_INFO_SCRIPT)):
            identifier = command.rsplit(" ", 1)[-1]
            return json.dumps(PACKAGE_DEPENDENCY_MAPPING[identifier])

        elif command.startswith("python -m pip show"):
            name = re.search(r"'(.+)'", command).group(1)
            return METADATA_MAPPING[name]

    mocker.patch.object(qip.command, "execute", _command_execute)


@pytest.fixture(autouse=True)
def mock_system(mocker):
    """Mock system mapping"""
    mocker.patch.object(
        qip.system, "query",
        return_value={
            "platform": "linux",
            "arch": "x86_64",
            "os": {
                "name": "centos",
                "major_version": 7
            }
        }
    )
