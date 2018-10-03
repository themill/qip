.. _release/release_notes:

*************
Release Notes
*************

.. release:: Upcoming

    .. change:: new

        Write out a `packages.txt` file to the output path, which contains a
        list of packages installed by the last run.

        This file is a temporary file to assist batch installing the packages
        into a :term:`Wiz` registry without having to manually keep track of
        which dependencies got installed.

        The format is::

            "/tmp/foo/foo-0.1.0"
            "/tmp/bar/bar-2.3.0"

    .. change:: new

        Write out a :term:`Wiz` definition into package directories, describing
        the system requirements, name, description, version and possible
        requirements that package has. The file will be in the same directory
        as the install and be called after the package, ie. `foo-0.1.0.json`

        .. seealso::

            The format is a normal :term:`Wiz` :ref:`Package Definition
            <wiz:definition>`.

    .. change:: new

        Rewrite of qip functionality. Only installs packages locally.


.. release:: 0.1.0

    .. change:: new

        Initial release.
