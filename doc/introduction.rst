.. _introduction:

************
Introduction
************

qip is a Quarantine Installer for Python. It is capable of installing and downloading
packages to specific locations in an isolated manner. Each package has a top
level directory under the install directory. Inside this directory
are the versions for each package. The purpose for this is to enable wiz to
resolve clean environments using only the packages required by the wiz environment.

qip does this by wrapping pip commands to query and install packages.
When installing a package qip will resolve the package's dependencies and install those too.

Resulting pacakge installation will look like this:

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

