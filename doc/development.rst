.. _development:

******************
Python Development
******************

Development with Qip and Wiz
============================

When developing Python modules, it is usually desired to be able to install
the module in editable mode, directly linking to the source code for rapid
development.

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

    > wiz -dsp /tmp/qip/definitions use foo -- foo

.. hint::

    A module can be installed without dependencies, especially if they are
    already available in a global registry.
    However, any requirement the module has, needs to be available in the
    registries visible to :term:`Wiz`, when resolving the request, so additional
    :option:`qip install --definition-path` might need to be set.

Definitions
-----------
Since it has been installed in editable mode, foo's definition needs have a
PYTHONPATH set to the source.

Default definition
^^^^^^^^^^^^^^^^^^

If foo is a module without a custom definition in its repository, a default one
is being created, including:

- entry points for 'commands'
- dependencies for 'requirements'
- path to the source as "PYTHONPATH"

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
retrieve that and update it with:

- entry points for 'commands'
- dependencies for 'requirements'
- path to the source as 'install-location'

For example::

    {
        "identifier": "foo",
        "command": {
            "foo": "python -m foo"
        },
        "environ": {
            "EXTRA": "1",
            "PYTHONPATH": "/some/path:${INSTALL_LOCATION}:${PYTHONPATH}",
            "MAYA_SCRIPTS_PATH": "${INSTALL_LOCATION}/package_data/maya:${MAYA_SCRIPTS_PATH}"
        },
        "install-location": "~/dev/foo/source",
        "requirements: [
             "maya",
             "bar"
        ]
    }

.. note::

    This means, that the custom definition inside the repository only needs to
    include environment variables, requirements and command aliases, if they
    are special.

    For example, this could be the `wiz.json` inside of foo for the example
    above::

        {
            "identifier": "foo",
            "environ": {
                "EXTRA": "1",
                "PYTHONPATH": "/some/path:${INSTALL_LOCATION}:${PYTHONPATH}",
                "MAYA_SCRIPTS_PATH": "${INSTALL_LOCATION}/package_data/maya:${MAYA_SCRIPTS_PATH}"
            },
            "requirements: [
                 "maya"
            ]
        }
