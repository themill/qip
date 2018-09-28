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
from packaging.requirements import Requirement

import qip.package
import qip.filesystem

from ._version import __version__


def install(
    requests, output_path, overwrite_packages=False, no_dependencies=False
):
    """Install packages to *output_path* from *requests*.

    * *requests* should be a list of packages that should be installed.
    * *output_path* should be the destination installation path.
    * *overwrite_packages* should indicate whether packages already installed
    should be overwritten. If None, a user confirmation will be prompted.
    Default is False.
    * *no_dependencies* should indicate whether package dependencies should be
    skipped. Default is False.

    """
    logger = mlog.Logger(__name__ + ".install")

    qip.filesystem.ensure_directory(output_path)

    # Setup temporary folder for package installation.
    temporary_path = tempfile.mkdtemp()
    install_path = os.path.join(
        temporary_path, "lib", "python2.7", "site-packages"
    )

    # Update environment mapping.
    environ_mapping = fetch_environ(mapping={"PYTHONPATH": install_path})

    # Record package identifiers to prevent duplication
    package_identifiers = set()

    # Fill up queue with requirements extracted from requests.
    queue = _queue.Queue()
    for request in requests:
        queue.put(Requirement(request))

    while not queue.empty():
        requirement = queue.get()

        try:
            package_mapping = qip.package.install(
                requirement, temporary_path, environ_mapping
            )
        except RuntimeError as error:
            logger.error(error)
            continue

        # Install package to destination.
        copy_to_destination(
            package_mapping,
            temporary_path,
            output_path,
            overwrite_packages
        )

        package_identifiers.add(package_mapping["identifier"])

        # Fill up queue with requirements extracted from package dependencies.
        if not no_dependencies:
            for mapping in package_mapping.get("requirements", []):
                if mapping["identifier"] in package_identifiers:
                    continue

                _requirement = Requirement(mapping["request"])
                queue.put(_requirement)

                package_identifiers.add(mapping["identifier"])

        # Clean up for next installation.
        logger.debug("Clean up directory content")
        qip.filesystem.remove_directory_content(temporary_path)


def copy_to_destination(
    package_mapping, source_path, destination_path, overwrite_packages=False
):
    """Copy package from *source_path* to *destination_path*.

    * *package_mapping* should be a mapping of the python package built.
    * *source_path* should be the path where the package was built
    * *destination_path* should be the installation path
    * *overwrite_packages* should indicate whether packages already installed
    should be overwritten. If None, a user confirmation will be prompted.
    Default is False.

    """
    logger = mlog.Logger(__name__ + ".copy_to_destination")

    name = package_mapping["name"]
    identifier = package_mapping["identifier"]

    target = os.path.join(destination_path, name)
    full_target = os.path.join(target, identifier)

    if os.path.isdir(full_target):
        if overwrite_packages is None:
            overwrite_packages = click.confirm(
                "Overwrite '{}'?".format(identifier)
            )

        if overwrite_packages:
            logger.warning(
                "Overwrite '{}' which is already installed.".format(identifier)
            )
            shutil.rmtree(full_target)

        else:
            logger.warning(
                "Skip '{}' which is already installed.".format(identifier)
            )
            return

    qip.filesystem.ensure_directory(target)
    shutil.copytree(source_path, full_target)

    logger.info("Installed {}.".format(identifier))


def fetch_environ(mapping=None):
    """Fetch mapping with all environment variables needed.

    * *mapping* can be a custom environment mapping which will be added to
    the initial environment.

    """
    logger = mlog.Logger(__name__ + ".fetch")

    logger.debug("initial environment: {}".format(mapping))

    if mapping is None:
        mapping = {}

    context = wiz.resolve_context(["python==2.7.*"], environ_mapping=mapping)

    # Extract environment mapping from context
    return context["environ"]
