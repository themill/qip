# :coding: utf-8

import os
import sys


def _lib_destination():
    """Return lib destination depending on the Python version."""
    name = "python{major}.{minor}".format(
        major=sys.version_info.major,
        minor=sys.version_info.minor,
    )
    return os.path.join("lib", name, "site-packages")


#: Variable symbol for :term:`Wiz` definition environment.
INSTALL_LOCATION = "${INSTALL_LOCATION}"

#: Variable symbol for :term:`Wiz` definition environment.
INSTALL_ROOT = "${INSTALL_ROOT}"

#: :term:`Wiz` request to resolve :term:`Python` 2.7 environment.
P27_REQUEST = "python==2.7.*"

#: Relative path to installed libraries in :term:`Python`.
LIB_DESTINATION = _lib_destination()
