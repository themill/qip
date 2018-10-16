.. _tutorial:

********
Tutorial
********

Installing a package
====================

To install a package simply issue the `qip install` command and specify
an output directory with `-o` or `--outdir`

For example:

.. code-block:: bash

    $> qip install -o /tmp/my_installs flask

Qip will then proceed to resolve dependencies and install the packages as
required.

If you want to install a single package without any of its dependencies, you
can pass the `--no-dependencies` argument to the install command.

.. code-block:: bash

    $> qip install -o /tmp/my_installs --no-dependencies flask

If you are installing a package that already exists, then you will be asked if
you want to overwrite it.

The various packages will be installed into the output directory inside a
package directory and finally into a version subdirectory. For example:

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

Definition
----------

Along with the install, a :term:`Wiz` :ref:`Package Definition <wiz:definition>`
file will be exported, which details information and dependencies of the
package. It is exported into the versioned directory and called after the
package, ie. `foo-0.1.0.json`.

To make a package installed with Qip usable inside of :term:`Wiz`, it has to be
installed into a :term:`Wiz` :ref:`Registry <wiz:registry>`.

Using the API
=============

qip can be used as an API by importing the `qip <api_reference/index.html>`__
module. For example to install a package::

    import qip

    qip.install(["foo"], "/path")

This will install the given package with its dependencies.

In order to install a package without its dependencies you should first call the
command with the `no_dependencies`::

    import qip

    qip.install(["foo"], "/path", no_dependencies=True)
