.. _tutorial:

********
Tutorial
********

Installing a package
--------------------

To install a package simply issue the `qip` command and specify
an output directory with `-o` or `--outdir`

For example:

.. code-block:: bash

    $> qip -o /tmp/my_installs flask

qip will then proceed to resolve dependencies and install the packages as required.

If you want to install a single package without any of its dependencies, you
can pass the `--nodeps` argument to the install command

.. code-block:: bash

    $> qip -o /tmp/my_installs --nodeps flask

If you are installing a package that already exists, then you will asked if you
want to overwrite it. You can skip these prompts and assume "yes" with the `-y`
option.

The various packages will be installed into the output directory inside a package
directory and finally into a version subdirectory. For example:

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

Along with the install, a requirements file will be written that details the
dependencies of the package. This will be written into the versioned directory
and called `requirements.json`. Its format will be something like this:

.. code:: json

            [
                {
                    "MarkupSafe": "/tmp/installs/MarkupSafe/MarkupSafe-1.0"
                }
            ]

Wiz can make use of these files to generate its own config files.

Using qip as an API
-------------------

qip can be used as an API by importing the `core API
<api_reference/core.html#core>`__ module. For example to install a package

.. code:: python

    from core import Qip

    qip = Qip("/install/directory", logger=mloginstance)
    qip.install_package("flask", ">=0.1.0", True)

This will only install the given package without its dependencies. In order
to fetch the dependencies you should first call ``fetch_dependencies`` and then
install each package separately.

An install will also populate
`Qip.dependency_tracker <api_reference/core.html#qip.core.Qip.dependency_tracker>`__

.. code:: python

    from core import Qip

    qip = Qip("/install/directory", logger=mloginstance)
    deps = {}
    qip.fetch_dependencies("flask==0.4.0", deps)

    for package, specs in deps.iteritems():
        specs = ",".join((x[0]+x[1] for x in specs))
        output, ret_code = qip.install_package(package, specs, kwargs["y"])

