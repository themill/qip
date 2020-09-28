.. _release/migration:

***************
Migration notes
***************

This section will show more detailed information when relevant for switching to
a new version, such as when upgrading involves backwards incompatibilities.

.. _release/migration/2.1.0:

Migrate to 2.1.0
================

.. rubric:: Handling Wiz registries

Qip is now automatically including default :term:`Wiz` registries to determine
whether the installation of a Python package should be skipped or if its
definition should be updated.

If using the command line, use :option:`-I/--ignore-registries
<qip install -I>` to prevent including default :term:`Wiz` registries.

.. rubric:: Handling Errors

Default installation process has been modified to raise an error when the
installation of a package has failed. Previously, the error was logged and the
installation process would resume.

If using the command line, use :option:`-R/--continue-on-error
<qip install -R>` to resume the installation without raising an error.

If using :func:`qip.install`, set the `continue_on_error` option to False.

.. rubric:: API

Signature of :func:`qip.install` has been modified to handle the process of
fetching a definition mapping from registry paths.

.. extended-code-block:: python
    :icon: ../image/avoid.png

    definition_mapping = wiz.fetch_definition_mapping(registry_paths)
    qip.install(["foo"], definition_mapping=definition_mapping)

.. extended-code-block:: python
    :icon: ../image/prefer.png

    qip.install(["foo"], registry_paths=registry_paths)

The following function has been renamed for consistency with
:func:`qip.definition.fetch_existing` :

* :func:`qip.definition.retrieve` → :func:`qip.definition.fetch_custom`

.. _release/migration/2.0.0:

Migrate to 2.0.0
================

.. rubric:: Project name

Project name has been changed to ``qip-installer`` to guarantee a unique name on
`Pypi <https://pypi.org/>`_.

.. rubric:: API

Following modules have been removed as logic can be used from the :mod:`wiz`
library instead:

* :mod:`qip.filesystem`
* :mod:`qip.symbol`
