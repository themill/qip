.. _release/migration:

***************
Migration notes
***************

This section will show more detailed information when relevant for switching to
a new version, such as when upgrading involves backwards incompatibilities.

.. _release/migration/2.1.0:

Migrate to 2.1.0
================

Default installation process has been modified to raise an error when the
installation of a package has failed. Previously, the error was logged and the
installation process would resume.

If using the command line, use :option:`qip install -R/--continue-on-error
<qip install -R>` to resume the installation without raising an error.

If using :func:`qip.install`, set the `continue_on_error` option to False.

.. _release/migration/2.0.0:

Migrate to 2.0.0
================

.. rubric:: project name

Project name has been changed to ``qip-installer`` to guarantee a unique name on
`Pypi <https://pypi.org/>`_.

.. rubric:: API

Following modules have been removed as logic can be used from the :mod:`wiz`
library instead:

* :mod:`qip.filesystem`
* :mod:`qip.symbol`
