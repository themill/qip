.. _release/release_notes:

*************
Release Notes
*************

.. release:: 2.4.1
    :date: 2021-05-21

    .. change:: fixed

        Fixed :func:`qip.definition.fetch_custom` to prevent systematically
        overwriting :ref:`identifier <wiz:definition/identifier>` from
        :ref:`custom definitions <development/custom_definition>`.

.. release:: 2.4.0
    :date: 2021-05-20

    .. change:: new

        Added :ref:`development/optional_dependencies`.

    .. change:: changed

        Updated :func:`qip.definition.fetch_custom` to always override
        :ref:`identifier <wiz:definition/identifier>` and :ref:`version
        <wiz:definition/version>` keywords with accurate information from the
        Python package. It means that it is no longer compulsory to add the
        identifier to :ref:`custom definitions <development/custom_definition>`.

    .. change:: changed

        Updated :func:`qip.definition.fetch_custom` to look for custom
        definitions matching :term:`extra keywords <extras_require>` provided in
        the request.

    .. change:: changed

        Updated :ref:`development/custom_definition`.

    .. change:: fixed

        Updated :func:`qip.definition.update` to better combine additional
        variants with variants found in custom :term:`Wiz` definition.

.. release:: 2.3.0
    :date: 2021-03-30

    .. change:: changed

        Updated :func:`qip.package.extract_identifier` to compute unique
        identifier which includes :term:`extra keywords <extras_require>`
        provided in the request. This ensures that packages installed with
        optional dependencies do not overwrite existing packages installed
        without optional dependencies or with different optional dependencies.

    .. change:: changed

        Added :func:`qip.package.extract_key` to compute unique package key
        which includes :term:`extra keywords <extras_require>` provided in the
        request. As package key is used to compute identifier of the
        corresponding :term:`Wiz` definition, it ensures that definitions
        installed with optional dependencies do not overwrite existing
        definitions installed without optional dependencies or with different
        optional dependencies.

    .. change:: changed

        Updated :func:`qip.package.extract_command_mapping` to extract commands
        from functions defined as ``console_scripts`` based on provided
        :term:`extra requirement keywords <extras_require>`

    .. change:: changed

        Updated :func:`qip.package.install` to properly convert private Git
        URLs from ``git@host:group/project.git`` to
        ``git+ssh://host/group/git+ssh://``.

        .. seealso::

            `PIP Documentation - Git support
            <https://pip.pypa.io/en/stable/reference/pip_install/#git>`_

.. release:: 2.2.0
    :date: 2020-11-04

    .. change:: changed

        Updated repository to use built-in :mod:`logging` module instead of
        `sawmill <https://gitlab.com/4degrees/sawmill>`_ as there are no clear
        advantages in using a non-standard framework to handle logging.

.. release:: 2.1.1
    :date: 2020-09-28

    .. change:: fixed

        Updated :func:`qip.install` to prevent skipping installation when
        editable mode is used, even if a package version is found in :term:`Wiz`
        registries.

        .. seealso:: :ref:`development/editable`

.. release:: 2.1.0
    :date: 2020-09-26

    .. change:: changed
        :tags: command-line

        Updated installation process to automatically include default
        :term:`Wiz` registries to determine whether the installation of a Python
        package should be skipped or if its definition should be updated.

        Added :option:`-I/--ignore-registries<qip install -I>` to ignore default
        :term:`Wiz` registries.

    .. change:: changed
        :tags: API

        Updated :func:`qip.install` to handle the process of fetching a
        definition mapping from registry paths. It spares the user from having
        to fetch definition mapping and makes the usage simpler.

    .. change:: changed
        :tags: API

        Updated :func:`qip.install` to skip installation when a package version
        is found in :term:`Wiz` registries.

    .. change:: new
        :tags: command-line

        Added :option:`qip install -R/--continue-on-error <qip install -R>` to
        resume the installation process when a package fails to install. By
        default, an error is raised.

    .. change:: changed
        :tags: API

        Updated :func:`qip.install` with `continue_on_error` option to
        indicate whether installation process should resume when a package
        fails to install. Default is False.

    .. change:: new
        :tags: API

        Added :func:`qip.definition.fetch_existing` to fetch a Python package in
        a definition mapping.

    .. change:: changed
        :tags: API

        Renamed :func:`qip.definition.retrieve` to
        :func:`qip.definition.fetch_custom` for consistency with
        :func:`qip.definition.fetch_existing`.

    .. change:: fixed
        :tags: API

        Fixed :func:`qip.install` to apply ``editable_mode`` for all incoming
        requests. Previously, it would only apply to the first request.

.. release:: 2.0.2
    :date: 2020-09-15

    .. change:: fixed

        Updated :func:`qip.definition.export` to target specific package version
        when retrieving additional variants which will be included in the
        definition to export.

.. release:: 2.0.1
    :date: 2020-09-14

    .. change:: new

        Added configuration to run unit tests on `Travis
        <https://travis-ci.org/themill/qip>`_

    .. change:: new

        Added configuration to build documentation on `ReadTheDocs
        <https://qip.readthedocs.io/en/stable/>`_

.. release:: 2.0.0
    :date: 2020-09-14

    .. change:: changed

        Project name has been changed to ``qip-installer`` to guarantee a unique
        name on :term:`PyPi`.

    .. change:: changed

        Updated dependency to the major version 3 of :term:`Wiz`.

    .. change:: changed

        Updated the following modules to add compatibility with python 3.7 and
        3.8:

        * :mod:`qip`
        * :mod:`qip.definition`
        * :mod:`qip.system`

    .. change:: new

        Added following short options:

        * :option:`qip install -N` for :option:`qip install --no-dependencies`
        * :option:`qip install -u` for :option:`qip install --update`
        * :option:`qip install -f` for :option:`qip install --overwrite-installed`
        * :option:`qip install -s` for :option:`qip install --skip-installed`

    .. change:: changed

        Updated :ref:`command_line` so that default values can be defined using
        :term:`Wiz` configuration file.

        ..  seealso:: :ref:`configuration`

    .. change:: changed

        Updated default value for :option:`-p/--python <qip install --python>`
        to use current :data:`Python executable <sys.executable>` instead of
        "python==2.7.*".

    .. change:: fixed

        Updated :func:`qip.environ.fetch` to link Python executable into an
        isolated temporary folder before using it and create an additional
        "python" symlink if needed. It is to ensure that no other Python
        executables installed in the same location is being accidentally picked
        up.

    .. change:: changed

        Removed :mod:`qip.filesystem` and :mod:`qip.symbol` and use logic from
        :mod:`wiz.filesystem` and :mod:`wiz.symbol` instead.

    .. change:: changed

        Removed ``mlog`` dependency and added :mod:`qip.logging` using
        :mod:`sawmill` directly to have more flexibility to configure the
        :class:`qip.logging.Logger` instance.

    .. change:: changed

        Updated repository to use `versup
        <https://versup.readthedocs.io/en/latest/>`_ the help with the release
        process.

.. release:: 1.8.1
    :date: 2020-04-01

    .. change:: fixed

        Updated :func:`qip.package.install` and
        :func:`qip.package.fetch_mapping_from_environ` to execute :term:`Pip`
        commands with `python -m pip
        <https://docs.python.org/2/using/cmdline.html#cmdoption-m>`_ instead
        of using the execution wrapper. Previously, it was picking up local
        version of the :term:`Pip` execution wrapper instead of using the one
        installed within the Python resolved environment.

.. release:: 1.8.0
    :date: 2019-04-04

    .. change:: changed

        Updated :func:`qip.install` to continue installing required packages
        even if the parent package is skipped during the :func:`copy process
        <copy_to_destination>`.

    .. change:: fixed

        Updated :func:`qip.install` to always clear the content of the
        temporary installation directory before installing a package.
        Previously, the temporary installation directory would be cleared after
        the installation, but this step would be skipped is the package
        installation was discarded.

    .. change:: fixed

        Updated :func:`qip.package.install` to use quotes when creating the
        :term:`Pip` subprocess command with the request. Previously it would
        fail to process a request with spaces (e.g. 'foo >= 1, < 2').

    .. change:: fixed

        Updated logging to avoid prints about a package being installed when it
        is actually being discarded.

.. release:: 1.7.0
    :date: 2019-04-03

    .. change:: changed
        :tags: definition

        Updated :func:`qip.definition.retrieve` to fetch custom :term:`Wiz`
        definition from the package installation location::

            <location>/foo/package_data/wiz.json

        Previously, it was assumed that the :file:`wiz.json` file would be
        located outside of the source (in :file:`share/wiz/wiz.json`), but it
        was impossible to distribute within a `wheel distribution
        <https://pythonwheels.com/>`_.

    .. change:: changed
        :tags: API, backwards-incompatible

        Updated :func:`qip.definition.export` to remove the now redundant
        "package_path" option.

    .. change:: changed
        :tags: API, backwards-incompatible

        Updated :func:`qip.definition.retrieve` to remove the now redundant
        "path" option.

.. release:: 1.6.0
    :date: 2019-04-01

    .. change:: changed
        :tags: API

        Updated :func:`qip.definition.update` to append previous
        :envvar:`PYTHONPATH` value to :envvar:`INSTALL_LOCATION` when updating
        the package definition.

.. release:: 1.5.0
    :date: 2019-04-01

    .. change:: changed
        :tags: definition

        Updated :func:`qip.definition.create` and :func:`qip.definition.update`
        to always add 'library' namespace to required Python packages fetched
        from the *setup.py* configuration file. Previously the extracted package
        was ambiguously named in the resulting package definition, which could
        lead :term:`Wiz` to not be able to resolve it properly

    .. change:: changed
        :tags: API

        Updated :func:`qip.definition.update` to add :envvar:`PYTHONPATH`
        to the definition :ref:`environment mapping <wiz:definition/environ>`
        in order to include the installed package.

.. release:: 1.4.0
    :date: 2019-03-28

    .. change:: changed
        :tags: API

        Updated :func:`qip.definition.create` and :func:`qip.definition.update`
        to add dependent Python packages as :ref:`requirements
        <wiz:definition/requirements>` which target the same Python version
        :ref:`variant <wiz:definition/variants>` (e.g. "foo[2.7]"). Previously,
        calling a package installed for several Python versions from :term:`Wiz`
        could take a long time as all variants would be tested in the resolution
        graph.

.. release:: 1.3.0
    :date: 2019-03-26

    .. change:: new
        :tags: command-line

        Added :option:`qip install --python` to target a specific Python version
        via a :term:`Wiz` request or a path to a Python executable.

    .. change:: new
        :tags: command-line

        Added :option:`qip install --update` to update :term:`Wiz` definition(s)
        that already exist in the :term:`Wiz` definitions output path with
        additional Python variants

    .. change:: new
        :tags: API

        Added :func:`qip.environ.fetch_python_mapping` to fetch information
        related to the Python version used within the environment :func:`fetched
        <qip.environ.fetch>`.

        A :mod:`qip.package_data.python_info` script is run within a
        subprocess to ensure that the Python version used by Qip could be
        different than the one used for the installation.

    .. change:: new
        :tags: API

        Added :func:`qip.fetch_context_mapping` to regroup all environment
        variables :func:`fetched <qip.environ.fetch>` and a mapping containing
        information about the Python version within a context mapping that
        can used during the installation process.

        The :envvar:`PYTHONPATH` environment variable is set to target
        the :mod:`site-packages <python:site>` directory within the package
        installation path.

    .. change:: new
        :tags: API

        Added :func:`qip.definition.export` to create and export a :term:`Wiz`
        definition for a specific Python package installed.

    .. change:: new
        :tags: API

        Added :func:`qip.package.is_system_required` to indicate whether a
        Python package is platform-specific. The logic was previously included
        in :func:`qip.package.extract_metadata_mapping` which has now been
        removed.

    .. change:: new
        :tags: API

        Added :func:`qip.package.extract_command_mapping` to retrieve all
        commands from a Python package. The logic was previously included
        in :func:`qip.package.extract_metadata_mapping` which has now been
        removed.

    .. change:: new
        :tags: API

        Added :func:`qip.package.extract_target_path` to always build the
        package folder destination with Python major and minor version in order
        to prevent names clashes. The logic was previously included in
        :func:`qip.package.fetch_mapping_from_environ`.

    .. change:: changed
        :tags: API, backwards-incompatible

        Updated :mod:`qip.definition` to embed :ref:`environment
        <wiz:definition/environ>` and :ref:`requirements
        <wiz:definition/requirements>` keywords within a :ref:`variant
        <wiz:definition/variants>` which is targeting the Python minor version
        that was used for the package installation.

        When a package is installed for another Python version, a new
        :ref:`variant <wiz:definition/variants>` will be added if required. When
        a :class:`~wiz.definition.Definition` instance has several variants, it
        will be sorted to have the highest Python version first, provided that
        the Python version is being used as a variant identifier.

    .. change:: changed
        :tags: API, backwards-incompatible

        Move :func:`qip.fetch_environ` to :func:`qip.environ.fetch` and add
        a "python_target" argument in order to target a specific Python version
        via a :term:`Wiz` request or a path to a Python executable.

    .. change:: changed
        :tags: API, backwards-incompatible

        Updated :func:`qip.definition.retrieve` to return a
        :class:`~wiz.definition.Definition` instance from a :file:`wiz.json`
        found in the Python package installation path without updating it as it
        was previously the case.

        The definition update is now handled by :func:`qip.definition.update`.

    .. change:: changed
        :tags: API, backwards-incompatible

        Removed :func:`qip.package.extract_metadata_mapping` and moved logic
        within :func:`qip.package.fetch_mapping_from_environ` instead for
        clarity.

    .. change:: changed
        :tags: API, backwards-incompatible

        Rename :mod:`qip.package_data.pip_query` to
        :mod:`qip.package_data.package_info` for consistency.

    .. change:: changed
        :tags: command-line

        Explicitly set the name of the program to "qip" instead of relying on
        :data:`sys.argv` in order to prevent "__main__.py" to be displayed when
        the command is being run as follows::

            python -m qip --help

.. release:: 1.2.1
    :date: 2019-02-04

    .. change:: fixed

        Removed unnecessary `sphinxcontrib-autoprogram
        <https://pypi.org/project/sphinxcontrib-autoprogram>`_ dependency.

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
        packages from :term:`PyPi` and set its value to 'library'.
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
        VCS projects in :ref:`editable mode <editable-installs>`.

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
        packages from :term:`PyPi`.

    .. change:: new
        :tags: definition

        Added :func:`qip.definition._update_install_location` to ensure that
        when retrieving a definition from a package, any occurrence of
        :envvar:`wiz:INSTALL_LOCATION` in a definition is being replaced with
        the accurate relative target path (including the identifier, version and
        potential system information). Without this adjustment, any path in
        :envvar:`wiz:INSTALL_LOCATION` retrieved from :term:`Devpi` would
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
        the package gets bundled and uploaded to :term:`Devpi`.

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
