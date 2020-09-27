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

The default :term:`Wiz` registries can be ignored with
:option:`-I/--ignore-registries <qip install -I>`.

.. rubric:: Installation with the API

:func:`qip.install` has been modified to handle the process of fetching a
definition mapping from registry paths.

.. extended-code-block:: python
    :icon: ../image/avoid.png

    definition_mapping = wiz.fetch_definition_mapping(registry_paths)
    qip.install(["foo"], definition_mapping=definition_mapping)

.. extended-code-block:: python
    :icon: ../image/prefer.png

    qip.install(["foo"], registry_paths=registry_paths)

The installation will be skipped when a package version is found in :term:`Wiz`
registries.

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
