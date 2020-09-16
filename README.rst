###
Qip
###

.. image:: https://img.shields.io/pypi/v/qip-installer.svg
    :target: https://pypi.python.org/pypi/qip-installer
    :alt: PyPi Package Link

.. image:: https://travis-ci.org/themill/qip.svg?branch=master
    :target: https://travis-ci.org/themill/qip
    :alt: Continuous Integration

.. image:: https://readthedocs.org/projects/qip/badge/?version=stable
    :target: https://qip.readthedocs.io/en/stable
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-LGPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/lgpl-3.0
    :alt: License Link

Qip is a Quarantine Installer for Python built over `Pip <https://pip.pypa.io>`_
and `Wiz <https://wiz.readthedocs.io/en/stable/index.html>`_.

It uses `Pip <https://pip.pypa.io>`_ commands to query and install Python
packages with its dependencies to specific locations in an isolated manner.

.. code-block:: bash

    >>> qip install scipy
    info: Requested 'scipy'
    info: 	Installed 'scipy-1.5.2'.
    info: 	Wiz definition created for 'scipy-1.5.2'.
    info: Requested 'numpy>=1.14.5' [from 'scipy-1.5.2'].
    info: 	Installed 'numpy-1.19.2'.
    info: 	Wiz definition created for 'numpy-1.19.2'.
    info: Packages installed: numpy-1.19.2, scipy-1.5.2
    info: Package output directory: '/tmp/qip/packages'
    info: Definition output directory: '/tmp/qip/definitions'

A `Wiz <https://wiz.readthedocs.io/en/stable/index.html>`_ definition is created
for each package installed in order to safely use it within a protected
environment.

.. code-block:: bash

    >>> wiz -add /tmp/qip/definitions use scipy -- python

*************
Documentation
*************

Full documentation, including installation and setup guides, can be found at
https://qip.readthedocs.io/en/stable/

*********
Copyright
*********

Copyright (C) 2018, The Mill

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
