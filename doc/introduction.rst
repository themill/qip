.. _introduction:

************
Introduction
************

Qip is a Quarantine Installer for Python built over :term:`Pip` and :term:`Wiz`.

It uses :term:`Pip` commands to query and install Python packages with its
dependencies to specific locations in an isolated manner.

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

A :term:`Wiz` definition is created for each package installed in order to
safely use it within a protected environment.

.. code-block:: bash

    >>> wiz -add /tmp/qip/definitions use scipy -- python

