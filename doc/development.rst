.. _development:

******************
Python Development
******************

Development with Qip and Wiz
============================

Allowing a Python module to be installed in editable mode, directly linking to
the source code, is important for rapid development.

To ensure that Qip/Wiz can provide the same functionality as pip installing
into a :term:`Virtualenv`, Qip supports an editable mode.

For this example it is assumed that `foo` is a python module that is pip
installable (includes a setup.py etc).

Qip can install this module and its dependencies::

    > cd foo
    > qip install -e .

The output packages can be found (by default) in::

    > cd /tmp/qip/packages

The output definitions can be found (by default) in::

    > cd /tmp/qip/definitions

Foo and all its dependencies should now be available to :term:`Wiz` through this
registry::

    > wiz -add /tmp/qip/definitions use foo -- foo

.. hint::

    A module can be installed without dependencies, especially if they are
    already available in a global registry.
    However, any requirement the module has, needs to be available in the
    registries visible to :term:`Wiz`, when resolving the request.

Definitions
-----------
Since it has been installed in editable mode, foo's definition needs have a
:envvar:`PYTHONPATH` set to the source code.

Default definition
^^^^^^^^^^^^^^^^^^

If foo is a module without a custom definition in its repository, a default one
is being created, including:

- :ref:`identifier <wiz:definition/identifier>`
- :ref:`namespace <wiz:definition/namespace>`
- :ref:`version <wiz:definition/version>`
- :ref:`description <wiz:definition/description>` from the setup.py
- entry points for :ref:`commands <wiz:definition/command>`
- dependencies from the setup.py for :ref:`requirements <wiz:definition/requirements>`
- path to the source as :ref:`install-location <wiz:definition/install_location>`

For example::

    {
        "identifier": "foo",
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "install-location": "~/dev/foo/source",
        "requirements: [
            "bar"
        ]
    }

Custom definition
^^^^^^^^^^^^^^^^^^

If foo is a module with a custom definition in its repository, :term:`Qip` will
retrieve that and update:

- :ref:`version <wiz:definition/version>`
- :ref:`namespace <wiz:definition/namespace>`
- :ref:`description <wiz:definition/description>` from the setup.py
- append entry points for :ref:`commands <wiz:definition/command>`
- append dependencies from the setup.py for :ref:`requirements <wiz:definition/requirements>`
- path to the source as :ref:`install-location <wiz:definition/install_location>`
- :envvar:`PYTHONPATH` in :ref:`environ <wiz:definition/environ>`

However, it will keep:

- :ref:`identifier <wiz:definition/identifier>`

For example, the custom definition :file:`wiz.json` could look like this::

    {
        "identifier": "foo",
        "command": {
            "bar": "python -m foo -- special"
        },
        "environ": {
            "EXTRA": "1",
            "MAYA_SCRIPTS_PATH": "${INSTALL_LOCATION}/package_data/maya:${MAYA_SCRIPTS_PATH}"
        },
        "requirements: [
             "maya"
        ]
    }

The resulting definition after the qip install could look like this::

    {
        "identifier": "foo",
        "version": "1.0.0",
        "namespace": "library",
        "command": {
            "foo": "python -m foo",
            "bar": "python -m foo -- special"
        },
        "environ": {
            "EXTRA": "1",
            "MAYA_SCRIPTS_PATH": "${INSTALL_LOCATION}/package_data/maya:${MAYA_SCRIPTS_PATH}"
        },
        "variants": [
            {
                "identifier": "2.7"
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements: [
                    "python >=2.7, <2.8",
                    "bar"
                ]
                "install-location": "~/dev/foo/source",
            }
        ]
        "requirements: [
             "maya"
        ]
    }

.. note::

    This means, that the custom definition inside the repository only needs to
    include environment variables, requirements and command aliases, if they
    are special.

.. important::

    When retrieving a definition, it is being assumed that the developer
    has set a :envvar:`PYTHONPATH` environment variable referencing
    :envvar:`INSTALL_LOCATION` in either :ref:`environ <wiz:definition/environ>`
    or in a :ref:`variant <wiz:definition/variants>` of the definition. It is
    **NOT** being added automatically, to ensure that the developer remains
    full control over the path order.

    Example::

        {
            "environ": {
                "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
            }
        }

Development for multiple Python versions
========================================

By default any Python package is build with Python 2.7.
If a package is required for multiple versions of Python, it should be build
sequentially, using the :option:`--update <qip install --update>` flag, i.e.:

    >>> qip install tensorflow
    >>> qip install tensorflow --python "python==3.6.*" --update

.. important::

    Installs using :option:`--update <qip install --update>` need to use the
    same :option:`--definition-path <qip install --definition-path>`, as it will
    look for definitions to update in there.

This will result in a definition like:

.. code-block:: python
    :emphasize-lines: 12, 23

    {
        "identifier": "tensorflow",
        "version": "1.13.1",
        "namespace": "library",
        "description": "TensorFlow is an open source machine learning framework for everyone.",
        "install-root": "/tmp/qip/packages",
        "command": {
            ...
        },
        "variants": [
            {
                "identifier": "3.6",
                "install-location": "${INSTALL_ROOT}/tensorflow/tensorflow-1.13.1-py36/lib/python3.6/site-packages",
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements": [
                    "python >=3.6, <3.7",
                    ...
                ]
            },
            {
                "identifier": "2.7",
                "install-location": "${INSTALL_ROOT}/tensorflow/tensorflow-1.13.1-py27/lib/python2.7/site-packages",
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                },
                "requirements": [
                    "python >=2.7, <2.8",
                    ...
                ]
            }
        ]
    }

This can also be used in editable mode, i.e::

    >>> cd {PATH_TO}/shadow && qip install -e ."[dev]"
    >>> wiz --add /tmp/qip/definitions use shadow -- pytest test
