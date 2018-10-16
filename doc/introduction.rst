.. _introduction:

************
Introduction
************

qip is a Quarantine Installer for Python.

It is capable of installing packages to specific locations in an isolated
manner. Each package has a top level directory under the install directory.
Inside this directory are the versions for each package.

Qip does this by wrapping :term:`Pip` commands to query and install packages.
When installing a package Qip will resolve the package's dependencies and
install those too.

The purpose for this is to enable :term:`Wiz` to resolve clean environments
using only the packages required and not relying on bundled :term:`Python`
contexts.

A package installation result will for example look like this:

.. code::

    <output directory>
    ├── flask
    │   └── flask-1.0.2
    │       ├── bin
    │       └── lib
    │           └── python2.7
    │               └── site-packages
    │                   ├── flask
    │                   │   └── json
    │                   └── Flask-1.0.2.dist-info

