# :coding: utf-8

from __future__ import print_function

import os
import tempfile
import shutil
try:
    import queue as _queue
except ImportError:
    import Queue as _queue

import wiz
import click
import mlog

import qip.definition
import qip.package
import qip.filesystem
import qip.symbol

from ._version import __version__


def install(
    requests, output_path, definition_path=None, overwrite=False,
    no_dependencies=False, editable_mode=False
):
    """Install packages to *output_path* from *requests*.

    :param requests: list of packages to be installed

        A request can be one of::

            ["."]
            ["/path/to/foo/"]
            ["foo", "bar"]
            ["foo==0.1.0"]
            ["foo >= 7, < 8"]
            ["git@gitlab:rnd/foo.git"]
            ["git@gitlab:rnd/foo.git@0.1.0"]
            ["git@gitlab:rnd/foo.git@dev"]

    :param output_path: data install path.
    :param definition_path: :term:`Wiz` definition install path. Default is
        None, which means that :term:`Wiz` definitions are not extracted.
    :param overwrite: indicate whether packages already installed and
        corresponding :term:`Wiz` definitions should be overwritten. If None, a
        user confirmation will be prompted. Default is False.
    :param no_dependencies: indicate whether package dependencies should be
        skipped. Default is False.
    :param editable_mode: install in editable mode. Default is False.

    """
    logger = mlog.Logger(__name__ + ".install")

    qip.filesystem.ensure_directory(output_path)
    if definition_path is not None:
        qip.filesystem.ensure_directory(definition_path)

    # Setup temporary folder for package installation.
    cache_dir = tempfile.mkdtemp()
    temporary_path = tempfile.mkdtemp()
    install_path = os.path.join(temporary_path, qip.symbol.P27_LIB_DESTINATION)

    # Needed for the editable mode.
    qip.filesystem.ensure_directory(install_path)

    try:
        # Update environment mapping.
        environ_mapping = fetch_environ(
            mapping={
                "PYTHONPATH": install_path,
                "PYTHONWARNINGS": "ignore:DEPRECATION"
            }
        )

        # Record requests and package installed to prevent duplications.
        installed_packages = set()
        installed_requests = set()

        # Fill up queue with requirements extracted from requests.
        queue = _queue.Queue()

        for request in requests:
            queue.put(request)

        while not queue.empty():
            request = queue.get()

            if request in installed_requests:
                continue

            try:
                package_mapping = qip.package.install(
                    request, temporary_path, environ_mapping, cache_dir,
                    editable_mode=editable_mode
                )

            except RuntimeError as error:
                logger.error(str(error))
                continue

            if package_mapping["identifier"] in installed_packages:
                continue

            installed_packages.add(package_mapping["identifier"])
            installed_requests.add(request)

            # Install package to destination.
            success, overwrite = copy_to_destination(
                package_mapping,
                temporary_path,
                output_path,
                overwrite=overwrite
            )

            if not success:
                continue

            # Extract a wiz definition is requested.
            if definition_path is not None:
                definition_data = qip.definition.retrieve(
                    package_mapping, temporary_path, output_path,
                    editable_mode=editable_mode
                )
                if definition_data is None:
                    definition_data = qip.definition.create(
                        package_mapping, output_path,
                        editable_mode=editable_mode
                    )

                wiz.export_definition(
                    definition_path, definition_data, overwrite=True
                )

            # Reset editable mode to False for requirements.
            editable_mode = False

            # Fill up queue with requirements extracted from package
            # dependencies.
            if not no_dependencies:
                for request in package_mapping.get("requirements", []):
                    queue.put(request)

            # Clean up for next installation.
            logger.debug("Clean up directory content")
            qip.filesystem.remove_directory_content(temporary_path)

    finally:
        shutil.rmtree(temporary_path)
        shutil.rmtree(cache_dir)


def copy_to_destination(
    package_mapping, source_path, destination_path, overwrite=False
):
    """Copy package from *source_path* to *destination_path*.

    Return a tuple with one boolean value indicating whether the copy has been
    done and one indicating a new value for the *overwrite* option.

    :param package_mapping: mapping of the python package built.
    :param source_path: path where the package was built.
    :param destination_path: path to install to.
    :param overwrite: indicate whether packages already installed should be
        overwritten. If None, a user confirmation will be prompted. Default is
        False.

    """
    logger = mlog.Logger(__name__ + ".copy_to_destination")

    identifier = package_mapping["identifier"]
    target = os.path.join(destination_path, package_mapping["target"])

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

            return False, overwrite_next

    qip.filesystem.ensure_directory(os.path.dirname(target))
    shutil.copytree(source_path, target)
    logger.debug("Source copied to '{}'".format(target))

    logger.info("Installed '{}'.".format(identifier))

    return True, overwrite_next


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


def fetch_environ(mapping=None):
    """Fetch mapping with all environment variables needed.

    :param mapping: optional custom environment mapping to be added to initial
        environment.

    """
    logger = mlog.Logger(__name__ + ".fetch")
    logger.debug("initial environment: {}".format(mapping))

    if mapping is None:
        mapping = {}

    context = wiz.resolve_context(
        [qip.symbol.P27_REQUEST], environ_mapping=mapping
    )

    return context["environ"]
