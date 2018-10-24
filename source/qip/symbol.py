# :coding: utf-8

import os


#: Variable symbol for :term:`Wiz` definition environment.
INSTALL_LOCATION = "${INSTALL_LOCATION}"

#: :term:`Wiz` request to resolve :term:`Python` 2.7 environment.
P27_REQUEST = "python==2.7.*"

#: Relative path to installed libraries in :term:`Python` 2.7.
P27_LIB_DESTINATION = os.path.join("lib", "python2.7", "site-packages")

#: Relative path to installed executables.
BIN_DESTINATION = "bin"
