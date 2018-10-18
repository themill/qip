.. _release/release_notes:

*************
Release Notes
*************

.. release:: Upcoming

    .. change:: new

        Added :option:`qip install --editable` to install local
        projects or :term:`VCS` projects in :ref:`editable mode
        <editable-installs>`.

    .. change:: new

        Added :option:`qip install --definition-path` to
        define a destination path for the :term:`Wiz` definitions created. No
        definitions are extracted if this option is missing.

    .. change:: new

        Added :mod:`qip.symbol` to regroup common symbols.

    .. change:: changed

        Renamed :option:`qip install --output <qip install --output-path>` to
        :option:`qip install --output-path` for consistency.

    .. change:: changed

        Updated :func:`qip.install` to add a 'editable_mode' argument which
        installs the first package in :ref:`editable mode <editable-installs>`.

    .. change:: changed

        Updated :func:`qip.install` to add a 'definition_path' argument which
        defines a destination for :term:`Wiz` definition extracted. No
        definitions are extracted if this argument is missing.

    .. change:: changed

        Updated :func:`qip.package.install` to add a 'editable_mode' argument
        which installs the package in :ref:`editable mode <editable-installs>`.

    .. change:: changed

        Changed :func:`qip.definition.create` to modify the installation prefix
        from ``${INSTALL_LOCATION}`` to
        ``${INSTALL_LOCATION}/<package_name>/<package_identifier>``

    .. change:: fixed

        Fixed :func:`qip.install` to record package identifiers and requests
        before processing it. It ensures that no package is processed more than
        once even if the installation process is skipped.

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
