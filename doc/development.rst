.. _development:

******************
Python Development
******************

Qip provide a few features to ease the development process.

.. _development/editable:

Editable mode
=============

Qip provides an editable mode to allow for rapid development when developing
a Python package::

    >>> qip install -e .

.. seealso::

    `Pip "Editable" installs
    <https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs>`_

Let's clone the popular `Pystache <https://github.com/defunkt/pystache>`_
repository to demonstrate this feature::

    >>> git clone https://github.com/defunkt/pystache.git
    >>> cd ./pystache
    >>> qip install -e .

The ``pystache`` definition will ensure that the :ref:`install-location
<wiz:definition/install_location>` value will target the cloned repository:

.. code-block:: json
    :emphasize-lines: 16

    {
        "identifier": "pystache",
        "version": "0.5.4",
        "namespace": "library",
        "description": "Mustache for Python",
        "command": {
            "pystache": "python -m pystache.commands.render",
            "pystache-test": "python -m pystache.commands.test"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "3.8",
                "install-location": "/path/to/pystache/",
                "requirements": [
                    "python >= 3.8, < 3.9"
                ]
            }
        ]
    }

It is then possible to execute the following command::

    >>> wiz -add /tmp/qip/definitions run pystache -- 'Hello {{world}}' '{"world": "everybody"}'
    info: Start command: python -m pystache.commands.render 'Hello {{world}}' '{"world": "everybody"}'
    Hello everybody

You can modify the :file:`pystache/commands/render.py` file to print a different
output and ensure that it works as expected::

    diff --git a/pystache/commands/render.py b/pystache/commands/render.py
    index 1a9c309..9738c5e 100644
    --- a/pystache/commands/render.py
    +++ b/pystache/commands/render.py
    @@ -88,7 +88,7 @@ def main(sys_argv=sys.argv):
             context = json.loads(context)

         rendered = renderer.render(template, context)
    -    print rendered
    +    print "test " + rendered

The command will then return::

    >>> wiz -add /tmp/qip/definitions run pystache -- 'Hello {{world}}' '{"world": "everybody"}'
    info: Start command: python -m pystache.commands.render 'Hello {{world}}' '{"world": "everybody"}'
    test Hello everybody

.. _development/optional_dependencies:

Optional dependencies
=====================

Qip supports :term:`extra keywords <extras_require>` provided in the request.
Many Python packages use this installation feature, like
`Gunicorn <https://docs.gunicorn.org/en/stable/install.html#extra-packages>`_.

    >>> qip install gunicorn[gevent]

When using extra keywords, the nature of the package installed is fundamentally
modified. Not only does it change the dependencies, but it could also change the
:term:`Entry-Points` created.

.. seealso::

    `Setuptools - Optional Dependencies
    <https://setuptools.readthedocs.io/en/latest/userguide/
    dependency_management.html#optional-dependencies>`_

To prevent name clashes, the :term:`Wiz` definition extracted will include the
list of sorted :term:`extra keywords <extras_require>` used within its
:ref:`identifier <wiz:definition/identifier>`::

    {
        "identifier": "gunicorn-event",
        ...
    }

.. _development/custom_definition:

Custom Wiz definition
=====================

A default :term:`Wiz` definition will be created for each Python packages to
install. It will contain:

* :ref:`identifier <wiz:definition/identifier>` based of the project name.
* :ref:`version <wiz:definition/version>` based on the package version.
* :ref:`description <wiz:definition/description>` based on the package description.
* :ref:`commands <wiz:definition/command>` based on entry points defined in
  :file:`setup.py`.
* :ref:`requirements <wiz:definition/requirements>` based on package
  dependencies.
* :ref:`install-location <wiz:definition/install_location>` based on relative
  library path.

It is possible to add a custom definition within the repository to extend this
:term:`Wiz` definition. The custom definition should be included in the source
code under :file:`package_data/wiz.json`.

Let's use again the `Pystache <https://github.com/defunkt/pystache>`_ repository
to demonstrate this feature::

    >>> git clone https://github.com/defunkt/pystache.git
    >>> cd ./pystache

Add the following definition in :file:`pystache/package_data/wiz.json`

.. code-block:: json

    {
        "command": {
            "say_hello": "python -m pystache.commands.render 'Hello {{world}}' '{\"world\": \"everybody\"}'"
        }
    }

Now install the definition as follows::

    >>> qip install .

It is then possible to execute the following command::

    >>> wiz -add /tmp/qip/definitions run say_hello
    info: Start command: python -m pystache.commands.render 'Hello {{world}}' '{"world": "everybody"}'
    Hello everybody

Using a custom definition could be particularly helpful when a Python package
depends on a non-Python library.

.. note::

    It is also possible to add optional custom definition matching
    :term:`extra keywords <extras_require>` provided in the request.
    For instance, if a non-Python library must be set as a dependency when the
    "gevent" keyword is passed when installing the
    `Gunicorn <https://docs.gunicorn.org/en/stable/install.html#extra-packages>`_
    library, a targeted definition can be set in
    :file:`gunicorn/package_data/wiz-gevent.json`.

.. _development/custom_definition/dcc:

Working with DCCs
-----------------

When writing a Python plugin for a Digital content creation tool, a custom
:term:`Wiz` definition should be used to ease the development and deployment
process.

Here are a few usage examples:

* `Maya (Autodesk) <https://www.autodesk.com/products/maya/overview>`_

.. code-block:: json

    {
        "identifier": "foo",
        "namespace": "maya",
        "environ": {
            "MAYA_PLUG_IN_PATH": "${INSTALL_LOCATION}/foo/package_data/maya/plugin:${MAYA_PLUG_IN_PATH}",
            "MAYA_SCRIPT_PATH": "${INSTALL_LOCATION}/foo/package_data/maya/script/mel:${MAYA_SCRIPT_PATH}",
            "PYTHONPATH": "${INSTALL_LOCATION}/foo/package_data/maya/script/python:${PYTHONPATH}"
        },
        "requirements": [
            "maya"
        ]
    }

* `Flame (Autodesk) <https://www.autodesk.com/products/flame/overview>`_

.. code-block:: json

    {
        "identifier": "foo",
        "namespace": "flame",
        "environ": {
            "DL_PYTHON_HOOK_PATH": "${INSTALL_LOCATION}/foo/package_data/python:${DL_PYTHON_HOOK_PATH}"
        },
        "requirements": [
            "flame"
        ]
    }

* `Nuke (Foundry) <https://www.foundry.com/products/nuke>`_

.. code-block:: json

    {
        "identifier": "foo",
        "namespace": "nuke",
        "environ": {
            "NUKE_PATH": "${INSTALL_LOCATION}/foo/package_data/nuke:${NUKE_PATH}"
        },
        "requirements": [
            "nuke"
        ]
    }

* `Houdini (SideFX) <https://www.sidefx.com/products/houdini>`_

.. code-block:: json

    {
        "identifier": "foo",
        "namespace": "houdini",
        "environ": {
            "HOUDINI_PATH": "${INSTALL_LOCATION}/foo/package_data/houdini:${HOUDINI_PATH}"
        },
        "requirements": [
            "houdini"
        ]
    }

* `RV (Shotgun) <https://www.shotgunsoftware.com/rv>`_

.. code-block:: json

    {
        "identifier": "foo",
        "namespace": "rv",
        "environ": {
            "RV_SUPPORT_PATH": "${INSTALL_LOCATION}/foo/package_data/rv:${RV_SUPPORT_PATH}"
        },
        "requirements": [
            "rv"
        ]
    }
