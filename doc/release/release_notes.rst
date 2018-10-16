.. _release/release_notes:

*************
Release Notes
*************

.. release:: 1.0.0
    :date: 2018-10-16

    .. change:: new

        Retrieve a :term:`Wiz` definition from an installed package, if there
        was one bundled with it.

        Any python package exporting a `wiz.json` to a shared location
        `/share/package-name/` on install, will cause Qip to _not_ create a new
        :term:`Wiz` definition from scratch. Instead the bundled definition
        will be renamed (ie. `foo-0.1.0.json`) and copied to the install location.

        There are no changes made to a retrieved :term:`Wiz` definition.
        Any dependencies or system information will have to be correct when
        the package gets bundled and uploaded to :term:`devpi`.

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
