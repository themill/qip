.. _deployment:

**********
Deployment
**********

When creating the :term:`Wiz` definitions corresponding to Python packages, Qip
will use the :ref:`install-root <wiz:definition/install_root>` keyword to target
the package installation path. The :ref:`install-location
<wiz:definition/install_location>` value targeting the path to the library is
relative to the :ref:`install-root <wiz:definition/install_root>` value.

Therefore, it relatively easy to install and deploy Python packages
on a `NFS share <https://en.wikipedia.org/wiki/Network_File_System>`_::

    # Install 'foo' and all its dependencies
    >>> qip install foo

    # Rsync all packages on an accessible NFS share
    >>> rsync -avzl /tmp/qip/packages/* remote:/path/to/python/packages

    # Modify Wiz definitions to target remote location
    >>> wiz edit -f --set install-root /path/to/python/packages /tmp/qip/definitions/*

    # Install Wiz definitions in a global registry
    >>> wiz install -r /path/to/registry /tmp/qip/definitions/*

