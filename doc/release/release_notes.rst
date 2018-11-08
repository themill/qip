.. _release/release_notes:

*************
Release Notes
*************

.. release:: Upcoming

    .. change:: fixed

        Used the 'package_name' instead of 'key' to match the package when
        retrieving the package information from 'pipdeptree', to make sure
        any packages with camelcase or underscores are taken into account.

.. release:: 1.1.1
    :date: 2018-10-25

    .. change:: fixed

        Fixed :func:`qip.install` to always overwrite the :term:`Wiz` package
        definition when the package is being overwritten for consistency.

.. release:: 1.1.0
    :date: 2018-10-24

    .. change:: new
        :tags: command-line

        Added :option:`qip install --editable` to install local projects or
        :term:`VCS` projects in :ref:`editable mode <editable-installs>`.

    .. change:: new
        :tags: command-line

        Added :option:`qip install --definition-path` to define a destination
        path for the :term:`Wiz` definitions created. No definitions are
        extracted if this option is missing.

    .. change:: new
        :tags: definition

        Added 'install-location' keyword when retrieving a definition from a
        package, if :envvar:`wiz:INSTALL_LOCATION` is used in any occurrence of
        ``environ``.

    .. change:: new
        :tags: definition

        Added 'group' keyword set to "python" when creating new definitions for
        packages from :term:`Pypi`.

    .. change:: new
        :tags: definition

        Added :func:`qip.definition._update_install_location` to ensure that
        when retrieving a definition from a package, any occurrence of
        :envvar:`wiz:INSTALL_LOCATION` in a definition is being replaced with
        the accurate relative target path (including the identifier, version and
        potential system information). Without this adjustment, any path in
        :envvar:`wiz:INSTALL_LOCATION` retrieved from :term:`devpi` would
        include non existent paths and the link to the data would be lost.

    .. change:: new
        :tags: API

        Added :mod:`qip.symbol` to group common symbols.

    .. change:: changed
        :tags: command-line

        Renamed :option:`qip install --output <qip install --output-path>` to
        :option:`qip install --output-path` for consistency.

    .. change:: changed
        :tags: API

        Updated :func:`qip.install` to add a 'editable_mode' argument which
        installs the first package in :ref:`editable mode <editable-installs>`.

    .. change:: changed
        :tags: API

        Updated :func:`qip.install` to add a 'definition_path' argument which
        defines a destination for :term:`Wiz` definition extracted. No
        definitions are extracted if this argument is missing.

    .. change:: changed
        :tags: API

        Updated :func:`qip.package.install` to add a 'editable_mode' argument
        which installs the package in :ref:`editable mode <editable-installs>`.

    .. change:: changed
        :tags: API

        Changed :func:`qip.definition.create` to modify the installation prefix
        from ``${INSTALL_LOCATION}`` to
        ``${INSTALL_LOCATION}/<package_name>/<package_identifier>``

    .. change:: fixed
        :tags: API

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
