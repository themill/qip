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

import qip.package
import qip.filesystem

from ._version import __version__


def install(
    requests, output_path, overwrite_packages=False, no_dependencies=False
):
    """Install packages to *output_path* from *requests*.

    :param requests: list of packages to be installed

        A request can be one of::

            "foo"
            "foo==0.1.0"
            "foo >= 7, < 8"
            "git@gitlab:rnd/foo.git"
            "git@gitlab:rnd/foo.git@0.1.0"
            "git@gitlab:rnd/foo.git@dev"

    :param output_path: destination installation path
    :param overwrite_packages: indicate whether packages already installed
        should be overwritten. If None, a user confirmation will be prompted.
        Default is False.
    :param no_dependencies: indicate whether package dependencies should be
        skipped. Default is False.

    """
    logger = mlog.Logger(__name__ + ".install")

    qip.filesystem.ensure_directory(output_path)

    # Setup temporary folder for package installation.
    temporary_path = tempfile.mkdtemp()
    install_path = os.path.join(
        temporary_path, "lib", "python2.7", "site-packages"
    )

    try:
        # Update environment mapping.
        environ_mapping = fetch_environ(mapping={"PYTHONPATH": install_path})

        # Record package identifiers to prevent duplication
        package_identifiers = set()

        # Fill up queue with requirements extracted from requests.
        queue = _queue.Queue()
        for request in requests:
            queue.put(request)

        installed_packages = []
        while not queue.empty():
            request = queue.get()

            try:
                package_mapping = qip.package.install(
                    request, temporary_path, environ_mapping
                )
            except RuntimeError as error:
                logger.error(error)
                continue

            if package_mapping["identifier"] in package_identifiers:
                continue

            # Install package to destination.
            installation_path = copy_to_destination(
                package_mapping,
                temporary_path,
                output_path,
                overwrite_packages
            )
            if installation_path is None:
                continue

            installed_packages.append(os.path.abspath(installation_path))

            # Extract a wiz definition within the same path.
            definition = retrieve_definition(package_mapping, temporary_path)
            if definition is None:
                create_package_definition(package_mapping, installation_path)
            wiz.export_definition(installation_path, definition)

            package_identifiers.add(package_mapping["identifier"])

            # Fill up queue with requirements extracted from package
            # dependencies.
            if not no_dependencies:
                for mapping in package_mapping.get("requirements", []):
                    if mapping["identifier"] in package_identifiers:
                        continue

                    queue.put(mapping["request"])

            # Clean up for next installation.
            logger.debug("Clean up directory content")
            qip.filesystem.remove_directory_content(temporary_path)

        if len(installed_packages):
            packages_file = export_packages_file(
                output_path, installed_packages
            )
            logger.info(
                "Exported installed packages log file: {!r}".format(
                    packages_file
                ))

    finally:
        shutil.rmtree(temporary_path)


def copy_to_destination(
    package_mapping, source_path, destination_path, overwrite_packages=False
):
    """Copy package from *source_path* to *destination_path*.

    Return the path to the installed package.

    :param package_mapping: mapping of the python package built
    :param source_path: path where the package was built
    :param destination_path: path to install to
    :param overwrite_packages: indicate whether packages already installed
        should be overwritten. If None, a user confirmation will be prompted.
        Default is False.

    """
    logger = mlog.Logger(__name__ + ".copy_to_destination")

    name = package_mapping["name"]
    folder_identifier = package_mapping["identifier"]

    if package_mapping.get("system"):
        os_mapping = package_mapping["system"]["os"]
        folder_identifier += "-{}{}".format(
            os_mapping["name"], os_mapping["major_version"]
        )

    target = os.path.join(destination_path, name)
    full_target = os.path.join(target, folder_identifier)

    if os.path.isdir(full_target):
        if overwrite_packages is None:
            overwrite_packages = click.confirm(
                "Overwrite '{}'?".format(folder_identifier)
            )

        if overwrite_packages:
            logger.warning(
                "Overwrite '{}' which is already installed.".format(
                    folder_identifier
                )
            )
            shutil.rmtree(full_target)

        else:
            logger.warning(
                "Skip '{}' which is already installed.".format(
                    folder_identifier
                )
            )
            return None

    qip.filesystem.ensure_directory(target)
    shutil.copytree(source_path, full_target)
    logger.debug("Source copied to '{}'".format(full_target))

    logger.info("Installed {}.".format(folder_identifier))
    return full_target


def fetch_environ(mapping=None):
    """Fetch mapping with all environment variables needed.

    :param mapping: optional custom environment mapping to be added to initial
        environment.

    """
    logger = mlog.Logger(__name__ + ".fetch")

    logger.debug("initial environment: {}".format(mapping))

    if mapping is None:
        mapping = {}

    context = wiz.resolve_context(["python==2.7.*"], environ_mapping=mapping)

    return context["environ"]


def create_package_definition(mapping, path):
    """Create :term:`Wiz` definition for package *mapping*.

    :param mapping: mapping of the python package built
    :param path: path to install the package definition to
    :returns: definition data

    """
    definition_data = {
        "identifier": mapping["key"],
        "version": mapping["version"],
        "install-location": path
    }

    if "description" in mapping.keys():
        definition_data["description"] = mapping["description"]

    if "system" in mapping.keys():
        major_version = mapping["system"]["os"]["major_version"]

        definition_data["system"] = {
            "platform": mapping["system"]["platform"],
            "arch": mapping["system"]["arch"],
            "os": (
                "{name} >= {min_version}, <{max_version}".format(
                    name=mapping["system"]["os"]["name"],
                    min_version=major_version,
                    max_version=major_version + 1,
                )
            )
        }

    if "requirements" in mapping.keys():
        definition_data["requirements"] = [
            _mapping["request"] for _mapping in mapping["requirements"]
        ]

    lib_path = os.path.join(path, "lib", "python2.7", "site-packages")
    if os.path.isdir(lib_path):
        definition_data.setdefault("environ", {})
        definition_data["environ"]["PYTHONPATH"] = (
            "{}:${{PYTHONPATH}}".format(
                os.path.join(
                    "${INSTALL_LOCATION}", "lib", "python2.7", "site-packages"
                )
            )
        )

    bin_path = os.path.join(path, "bin")
    if os.path.isdir(bin_path):
        definition_data.setdefault("environ", {})
        definition_data["environ"]["PATH"] = (
            "{}:${{PATH}}".format(os.path.join("${INSTALL_LOCATION}", "bin"))
        )

    return definition_data


def retrieve_definition(mapping, path):
    """Retrieve :term:`Wiz` definition from package install.

    :param mapping: mapping of the python package built
    :param path: path where the package was temporarily installed to
    :return: None if no definition was found, otherwise the definition
    """

    definition_path = os.path.join(
        path, "share", "wiz", mapping["name"], "wiz.json"
    )
    if not os.path.exists(definition_path):
        return None

    definition = wiz.load_definition(definition_path)

    return definition


def export_packages_file(path, dependencies):
    """Export a file listing the installed packages.

    :param path: should be the output path for the file.
    :returns: full path to exported package file.

    """
    path = os.path.join(path, "packages.txt")

    _dependencies = []
    for _dependency in dependencies:
        _dependencies.append(
            os.path.join(_dependency, os.path.basename(_dependency) + ".json")
        )

    with open(path, "w") as outfile:
        outfile.write("\n".join(_dependencies))

    return path
