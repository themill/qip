# :coding: utf-8

import os
import logging
import sys
import tempfile
import shutil

import six.moves
import click
import wiz
import wiz.filesystem

import qip.definition
import qip.package
import qip.environ

from qip._version import __version__


def install(
    requests, output_path, definition_path=None, overwrite=False,
    no_dependencies=False, editable_mode=False, python_target=sys.executable,
    registry_paths=None, update_existing_definitions=False,
    continue_on_error=False
):
    """Install packages to *output_path* from *requests*.

    :param requests: List of package requests to be installed.

        A request can be one of::

            ["."]
            ["/path/to/foo/"]
            ["foo", "bar"]
            ["foo==0.1.0"]
            ["foo >= 7, < 8"]
            ["git@gitlab:rnd/foo.git"]
            ["git@gitlab:rnd/foo.git@0.1.0"]
            ["git@gitlab:rnd/foo.git@dev"]

    :param output_path: Destination path for Python packages installation.

    :param definition_path: Destination path for :term:`Wiz` definitions
        automatically created for Python packages installed. Default is None,
        which means that no :term:`Wiz` definitions are created.

    :param overwrite: Indicate whether packages already installed in destination
        path and corresponding :term:`Wiz` definitions should be overwritten. If
        None, a user confirmation will be prompted. Default is False.

    :param no_dependencies: Indicate whether package dependencies should be
        skipped. Default is False.

    :param editable_mode: Indicate whether the Python package location should
        target the source installation package. Default is False.

    :param python_target: Target a specific Python version via a Wiz request or
        a path to a Python executable (e.g. "python==2.7.*" or
        "/path/to/bin/python"). Default is the path to the current Python
        executable.

    :param registry_paths: List of :term:`Wiz` registry paths to consider when
        fetching existing definitions to update or skip.

    :param update_existing_definitions: Indicate whether variants from existing
        definitions should be used when exporting new definitions.

    :param continue_on_error: Indicate whether installation process should
        continue if a package cannot be installed. Default is False.

    :raises: :exc:`RuntimeError` if a package cannot be installed and
        *continue_on_error* is set to False.

    :return: Boolean value indicating whether packages were installed.

    """
    logger = logging.getLogger(__name__ + ".install")

    wiz.filesystem.ensure_directory(output_path)
    if definition_path is not None:
        wiz.filesystem.ensure_directory(definition_path)

    # Fetch definition mapping to determining whether a package should be
    # skipped or updated.
    definition_mapping = wiz.fetch_definition_mapping(registry_paths or [])

    # Setup temporary folder for package installation.
    cache_path = tempfile.mkdtemp()
    package_path = tempfile.mkdtemp()

    # Record requests and package installed to prevent duplications.
    installed_packages = set()
    installed_requests = set()

    # Record packages skipped.
    skipped_packages = set()

    # Fill up queue with requirements extracted from requests.
    queue = six.moves.queue.Queue()

    try:
        # Fetch environment mapping and installation path.
        context_mapping = fetch_context_mapping(package_path, python_target)
        library_path = context_mapping["environ"]["PYTHONPATH"]

        for request in requests:
            queue.put((request, None, editable_mode))

        while not queue.empty():
            request, parent_identifier, _editable_mode = queue.get()
            if request in installed_requests:
                continue

            # Clean up before installation.
            shutil.rmtree(package_path)
            wiz.filesystem.ensure_directory(package_path)

            # Needed for the editable mode.
            wiz.filesystem.ensure_directory(library_path)

            package_mapping, overwrite = _install(
                request, output_path, context_mapping, definition_mapping,
                package_path, cache_path, installed_packages,
                definition_path=definition_path,
                overwrite=overwrite,
                editable_mode=_editable_mode,
                update_existing_definitions=update_existing_definitions,
                parent_identifier=parent_identifier,
                continue_on_error=continue_on_error
            )
            if package_mapping is None:
                continue

            installed_packages.add(package_mapping["identifier"])
            installed_requests.add(request)

            # Indicate if package was skipped.
            if package_mapping.get("skipped", False):
                skipped_packages.add(package_mapping["identifier"])

            # Fill up queue with requirements extracted from package
            # dependencies.
            if not no_dependencies:
                for request in package_mapping.get("requirements", []):
                    queue.put((request, package_mapping["identifier"], False))

    finally:
        shutil.rmtree(package_path)
        shutil.rmtree(cache_path)

    # Sort and filter packages installed.
    installed = sorted(
        (p for p in installed_packages if p not in skipped_packages),
        key=lambda _id: _id.lower()
    )

    if len(installed):
        logger.info("Packages installed: {}".format(", ".join(installed)))

    return len(installed_packages) > 0


def _install(
    request, output_path, context_mapping, definition_mapping,
    package_path, cache_path, installed_packages, definition_path=None,
    overwrite=False, update_existing_definitions=False, editable_mode=False,
    continue_on_error=False, parent_identifier=None,
):
    """Install single package to *output_path* from *request*.

    :param request: Package requests to be installed.

    :param output_path: root destination path for Python packages installation.

    :param context_mapping: Mapping containing environment and python mapping
        as returned by :func:`fetch_context_mapping`

    :param definition_mapping: mapping regrouping all available definitions as
        returned by :func:`wiz.fetch_definition_mapping`.

    :param package_path: Temporary path to install package from :term:`Pip`.

    :param cache_path: Temporary directory for the :term:`Pip` cache.

    :param installed_packages: Set grouping all Python package identifiers
        already installed to skip current installation if necessary.

    :param definition_path: Destination path for :term:`Wiz` definition
        automatically created for Python package installed. Default is None,
        which means that no :term:`Wiz` definition is created.

    :param overwrite: Indicate whether package already installed in destination
        path and corresponding :term:`Wiz` definition should be overwritten. If
        None, a user confirmation will be prompted. Default is False.

    :param editable_mode: Indicate whether the Python package location should
        target the source installation package. Default is False.

    :param update_existing_definitions: Indicate whether variants from existing
        definitions should be used when exporting new definitions.

    :param continue_on_error: Indicate whether installation process should
        continue if a package cannot be installed. Default is False.

    :param parent_identifier: Indicate Python package which triggered the
        *request*. Default is None.

    :raises: :exc:`RuntimeError` if a package cannot be installed and
        *continue_on_error* is set to False.

    :return: tuple with package mapping installed (or None is the installation
        couldn't be processed), and one boolean value indicating a new value for
        the *overwrite* option.

    .. note::

        Package mapping returned will have an additional "skipped" keyword
        set as True if existing definition has been found in default registries.


    """
    logger = logging.getLogger(__name__ + "._install")

    try:
        package_mapping = qip.package.install(
            request, package_path, context_mapping, cache_path,
            editable_mode=editable_mode
        )

    except RuntimeError as error:
        if not continue_on_error:
            raise

        prompt = "Request '{}' has failed".format(request)
        if parent_identifier is not None:
            prompt += " [from '{}']".format(parent_identifier)

        logger.error("{}:\n{}".format(prompt, error))
        return None, overwrite

    if package_mapping["identifier"] in installed_packages:
        return None, overwrite

    # Attempt to fetch custom definition from package and existing definition
    # from definition mapping.
    custom_definition = None
    existing_definition = None

    if definition_path is not None:
        custom_definition = qip.definition.fetch_custom(package_mapping)
        existing_definition = qip.definition.fetch_existing(
            package_mapping, definition_mapping,
            namespace=getattr(custom_definition, "namespace", None),
        )

        if not editable_mode and _skip_install(
            existing_definition, package_mapping, definition_path
        ):
            logger.warning(
                "Skip '{0[key]}[{0[python][identifier]}]=={0[version]}' "
                "which already exists in Wiz registries."
                .format(package_mapping)
            )
            package_mapping["skipped"] = True
            return package_mapping, overwrite

    prompt = "Requested '{}'".format(request)
    if parent_identifier is not None:
        prompt += " [from '{}']".format(parent_identifier)
    logger.info(prompt)

    # Install package to destination.
    skipped, overwrite = copy_to_destination(
        package_mapping, package_path, output_path,
        overwrite=overwrite
    )

    # Extract a wiz definition is requested.
    if not skipped and definition_path is not None:
        qip.definition.export(
            definition_path, package_mapping, output_path,
            editable_mode=editable_mode,
            existing_definition=(
                existing_definition if update_existing_definitions else None
            ),
            custom_definition=custom_definition
        )

    package_mapping["skipped"] = skipped
    return package_mapping, overwrite


def _skip_install(existing_definition, package_mapping, definition_path):
    """Indicate whether existing definition mandates installation to be skipped.

    Skip package installation if existing definition:

    1. Is not None;
    2. Doesn't have a variant for the current Python version used;
    3. Is not stored in registry where installation process will export new
      definitions.

    Point 3 will be handled by :func:`copy_to_destination`.

    """
    python_version = package_mapping["python"]["identifier"]

    if existing_definition is None:
        return False

    if not any(
        variant.identifier == python_version for variant
        in existing_definition.variants
    ):
        return False

    return existing_definition.registry_path != definition_path


def copy_to_destination(
    mapping, source_path, destination_path, overwrite=False
):
    """Copy package from *source_path* to *destination_path*.

    :param mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :param source_path: path where the package was built.

    :param destination_path: path to install to.

    :param overwrite: indicate whether packages already installed should be
        overwritten. If None, a user confirmation will be prompted. Default is
        False.

    :return: tuple with one boolean value indicating whether the copy has been
        skipped and one indicating a new value for the *overwrite* option.

    """
    logger = logging.getLogger(__name__ + ".copy_to_destination")

    identifier = mapping["identifier"]
    target = os.path.join(destination_path, mapping["target"])

    # By default, future overwrite request will the same as the present one.
    overwrite_next = overwrite

    if os.path.isdir(target):
        if overwrite is None:
            overwrite, overwrite_next = _confirm_overwrite(identifier)

        if overwrite:
            logger.warning(
                "Overwrite '{}' which is already installed.".format(identifier)
            )
            shutil.rmtree(target)

        else:
            logger.warning(
                "Skip '{}' which is already installed.".format(identifier)
            )

            return True, overwrite_next

    wiz.filesystem.ensure_directory(os.path.dirname(target))
    shutil.copytree(source_path, target)
    logger.debug("Source copied to '{}'".format(target))

    logger.info("\tInstalled '{}'.".format(identifier))

    return False, overwrite_next


def _confirm_overwrite(identifier):
    """Package overwrite confirmation prompt for *identifier*

    Return a tuple with one boolean value indicating whether *identifier* should
    be overwritten and one boolean indicating whether future packages should
    also be overwritten.

    """
    message = (
        "Overwrite '{}'? ([y]es, [n]o, [ya] yes to all, [na] no to all)"
        .format(identifier)
    )

    answer = click.prompt(
        message,
        type=click.Choice(["y", "n", "ya", "na"]),
        default="n",
        show_choices=False,
        show_default=False
    )

    overwrite = answer[0] == "y"
    overwrite_next = overwrite if "a" in answer else None
    return overwrite, overwrite_next


def fetch_context_mapping(path, python_target):
    """Return context mapping containing environment and python mapping.

    :param path: path where python package has been installed.

    :param python_target: Target a specific Python version via a Wiz request or
        a path to a Python executable (e.g. "python==2.7.*" or
        "/path/to/bin/python").

    :return: Context mapping.

        It should be in the form of::

            {
                "environ": {
                    "PATH": "/path/to/bin",
                    "PYTHONPATH": "/path/to/lib/python2.7/site-packages",
                },
                "python": {
                    "identifier": "2.7",
                    "request": "python >= 2.7, < 2.8",
                    "installation-target": "lib/python2.7/site-packages"
                }
            }

    """
    environ_mapping = qip.environ.fetch(
        python_target, mapping={"PYTHONWARNINGS": "ignore"}
    )

    # Fetch Python version mapping from environment
    python_mapping = qip.environ.fetch_python_mapping(environ_mapping)

    # Compute the installation path and add it to PYTHONPATH
    install_path = os.path.join(path, python_mapping["library-path"])
    environ_mapping["PYTHONPATH"] = install_path

    return {
        "environ": environ_mapping,
        "python": python_mapping
    }
