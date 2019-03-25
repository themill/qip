# :coding: utf-8

import os
import sys

import mlog
import wiz


def fetch(python, mapping=None):
    """Fetch mapping with all environment variables needed.

    :param python: Target a specific Python version via a Wiz request or a path
        to a Python executable (e.g. "python==2.7.*" or "/path/to/bin/python").
    :param mapping: optional custom environment mapping to be added to initial
        environment.

    """
    logger = mlog.Logger(__name__ + ".fetch")
    logger.debug("initial environment: {}".format(mapping))

    if mapping is None:
        mapping = {}

    # If a Python executable is provided, use it instead of the Wiz request.
    if os.path.isfile(python) or os.sep in python:
        environ_mapping = mapping.copy()
        environ_mapping.update({
            "PATH": "{}:${{PATH}}".format(os.path.dirname(python))
        })
        context = {"environ": environ_mapping}

    else:
        context = wiz.resolve_context([python], environ_mapping=mapping)

    return context["environ"]


def python_library_path():
    """Return relative library destination depending on the Python version.

    :returns: Corresponding path (e.g. "lib/python2.7/site-packages")

    """
    name = "python{major}.{minor}".format(
        major=sys.version_info.major,
        minor=sys.version_info.minor,
    )
    return os.path.join("lib", name, "site-packages")


def python_request_mapping():
    """Return mapping indicating the Python version required.

    :returns: mapping in the form of::

        {
            "identifier": "2.7",
            "request": "python >= 2.7, < 2.8"
        }

    """
    python_version = sys.version_info

    return {
        "identifier": "{major}.{minor}".format(
            major=python_version.major,
            minor=python_version.minor,
        ),
        "request": "python >= {major}.{minor}, < {major}.{next_minor}".format(
            major=python_version.major,
            minor=python_version.minor,
            next_minor=python_version.minor + 1
        )
    }
