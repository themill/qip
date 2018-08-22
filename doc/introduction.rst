.. _introduction:

************
Introduction
************

qip is a Quarantine Installer for Python. It is capable of installing and downloading
packages to specific locations in an isolated manner. Each package resides in its own
directory under the install directory. The purpose for this is to enable wiz to
resolve clean environments using only the packages required by the wiz environment.

qip does this by wrapping pip commands to query, download, and install packages. Packages
can either be downloaded or installed. When installing a package qip will resolve the
package's dependencies and install those too.

Resulting pacakge installation will look like this:

.. code::

	── flask-0.12.2
	│   ├── bin
	│   └── lib
	│       └── python2.7
	│           └── site-packages
	│               ├── flask
	│               │   └── json
	│               └── Flask-1.0.2.dist-info
	├── Flask-JSON
	│   └── lib
	│       └── python2.7
	│           └── site-packages
	│               └── Flask_JSON-0.3.2-py2.7.egg-info
	├── Flask-Migrate
	│   └── lib
	│       └── python2.7
	│           └── site-packages
	│               ├── flask_migrate
	│               │   └── templates
	│               │       ├── flask
	│               │       └── flask-multidb
	│               └── Flask_Migrate-2.1.1.dist-info
	├── Flask-SQLAlchemy
	│   └── lib
	│       └── python2.7
	│           └── site-packages
	│               ├── flask_sqlalchemy
	│               └── Flask_SQLAlchemy-2.3.2.dist-info

