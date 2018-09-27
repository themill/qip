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

    # Fill up queue with requirements extracted from requests.
    queue = _queue.Queue()
    for request in requests:
        queue.put(Requirement(request))

    while not queue.empty():
        requirement = queue.get()

        try:
            _package = qip.package.install(
                requirement, temporary_path, environ_mapping
            )
        except RuntimeError as error:
            logger.error(error)
            continue

        # Fill up queue with requirements extracted from package dependencies.
        if not no_dependencies:
            for dependency in _package.get("dependencies", []):
                request = dependency.get("key", "")
                if dependency.get("required_version"):
                    request += dependency.get("required_version")

                queue.put(Requirement(request))

        # Install package to destination.
        copy_to_destination(
            _package["package"]["package_name"],
            _package["package"]["installed_version"],
            temporary_path,
            output_path,
            overwrite_packages
        )

        # Clean up for next installation.
        logger.debug("Clean up directory content")
        qip.filesystem.remove_directory_content(temporary_path)


def copy_to_destination(
    package_name, version, source_path, destination_path,
    overwrite_packages=False
):
    """Copy package from *source_path* to *destination_path*.

    * *package_name* should be the name of the package (e.g. "Foo")
    * *version* should be the version of the package (e.g. "0.1.0")
    * *source_path* should be the path where the package was built
    * *destination_path* should be the installation path
    * *overwrite_packages* should indicate whether packages already installed
    should be overwritten. If None, a user confirmation will be prompted.
    Default is False.

    """
    full_package_name = qip.filesystem.sanitise_value(
        "{name}-{version}".format(
            name=package_name,
            version=version
        )
    )

    target = os.path.join(destination_path, package_name)
    full_target = os.path.join(target, full_package_name)

    if os.path.isdir(full_target):
        if overwrite_packages is None:
            overwrite_packages = click.confirm(
                "Overwrite '{}'?".format(full_package_name)
            )

        # Remove package previously installed if necessary.
        if overwrite_packages:
            shutil.rmtree(full_target)

        # Otherwise, indicate that copy should be skipped.
        return

    qip.filesystem.ensure_directory(target)
    shutil.copytree(source_path, full_target)


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
