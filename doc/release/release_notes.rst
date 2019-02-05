.. _release/release_notes:

*************
Release Notes
*************

.. release:: 1.2.0
    :date: 2019-02-04

    .. change:: new
        :tags: documentation

        Added :ref:`development` section.

    .. change:: changed
        :tags: definition

        Updated :mod:`qip.definition` to add
        :ref:`install-root <wiz:definition/install_root>` and
        :ref:`install-location <wiz:definition/install_location>` values when
        creating or retrieving a definition.

        When installing a package via the command line, the :ref:`install-root
        <definition/install_root>` value is being set by the
        :option:`qip install --output-path` command. In **editable** mode,
        no :ref:`install-root <wiz:definition/install_root>` value is added.

        The :ref:`install-location <wiz:definition/install_location>` value is
        being set to the actual python package location and is relative to the
        :ref:`install-root <wiz:definition/install_root>` value. In **editable**
        mode, that path is pointing at the source to ease development without
        having to reinstall the package.

        When retrieving a definition, it is being assumed that the developer
        has set a :envvar:`PYTHONPATH` environment variable referencing
        :envvar:`INSTALL_LOCATION` in either
        :ref:`environ <wiz:definition/environ>` or in a
        :ref:`variant <wiz:definition/variants>` of the definition. It is
        **NOT** being added automatically, to ensure that the developer remains
        full control over the path order.

        Example::

            {
                "environ": {
                    "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
                }
            }

    .. change:: changed
        :tags: package

        Updated :func:`qip.package.extract_dependency_mapping` to use
        :mod:`qip.package_data.pip_query` to extract package dependency instead
        of `pipdeptree <https://github.com/naiquevin/pipdeptree>`_ so that
        extra requirements are taken into account (e.g. 'foo[dev]').

    .. change:: changed
        :tags: package

        Updated :func:`qip.package.extract_metadata_mapping` to retrieve entry
        points from package to use as command aliases in the exported
        definitions (e.g. "python -m foo").

    .. change:: changed
        :tags: definition

        Updated :mod:`qip.definition` to use entry point python calls instead
        of executables to update :ref:`command <definition/command>` value.
        When retrieving a definition, the command aliases defined by the
        developer are preserved, but missing entry points are being added, if
        available.

    .. change:: changed
        :tags: definition

        Updated :mod:`qip.definition` to update :ref:`requirements
        <definition/requirements>` when retrieving a definition. Any
        requirements in the retrieved definitions are extended to ensure that
        the developer can add requirements that are not in the *setup.py*
        configuration file (e.g. "maya", "nuke", etc)

    .. change:: changed
        :tags: command-line

        Changed :option:`qip install --output-path` and
        :option:`qip install --definition-path` to default to temporary
        directories when no input has been specified.

    .. change:: changed

        Updated :func:`qip.install` and :func:`qip.copy_to_destination` to
        add a 'Yes to all' and 'No to all' options to the package confirmation
        prompt. The user can now decide to be asked for confirmation once for
        the overwriting process and apply the given value to all future
        packages.

    .. change:: changed
        :tags: definition

        Changed 'group' keyword to 'namespace' when creating new definitions for
        packages from :term:`Pypi` and set its value to 'library'.
        The 'group' keyword has been replaced in :term:`Wiz` 1.3.0.

    .. change:: changed

        Enforced the request name in lower case, to make sure any packages
        with upper or camel case are taken into account, similar to pip.

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
