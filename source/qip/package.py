# :coding: utf-8

from __future__ import print_function
import re
import sys
import json
import os

import mlog

import qip.command
import qip.filesystem
import qip.system


#: Compiled regular expression to detect request with extra option.
REQUEST_PATTERN = re.compile(r"(.*)\[(\w*)\]")


#: Path to the python package query script.
PACKAGE_QUERY_SCRIPT = os.path.join(
    os.path.dirname(__file__), "package_data", "pip_query.py"
)


def install(
    request, destination, environ_mapping, cache_dir, editable_mode=False
):
    """Install package in *destination* from *requirement*.

    :param request: package to be installed

        A request can be one of::

            "/path/to/foo/"
            "."
            "foo"
            "foo==0.1.0"
            "foo >= 7, < 8"
            "git@gitlab:rnd/foo.git"
            "git@gitlab:rnd/foo.git@0.1.0"
            "git@gitlab:rnd/foo.git@dev"

    :param destination: valid path to install all packages to
    :param environ_mapping: mapping of environment variables
    :param cache_dir: Temporary directory for the pip cache
    :param editable_mode: install in editable mode. Default is False.

    :raises RuntimeError: if pip fails to install
    :raises ValueError: if the package name can not be extracted from the
        request.
    :returns: mapping with information about the package, as returned by
        :func:`fetch_mapping_from_environ`.

    """
    logger = mlog.Logger(__name__ + ".install")

    if request.startswith("git@gitlab:"):
        request = "git+ssh://" + request.replace(":", "/")

    logger.info("Installing '{}'...".format(request))
    result = qip.command.execute(
        "pip install "
        "--ignore-installed "
        "--no-deps "
        "--prefix {destination} "
        "--no-warn-script-location "
        "--disable-pip-version-check "
        "--cache-dir {cache_dir} "
        "{editable_mode}" 
        "{requirement}".format(
            editable_mode="-e " if editable_mode else "",
            destination=destination,
            requirement=request,
            cache_dir=cache_dir
        ),
        environ_mapping
    )

    match_name = re.search("(?<=Installing collected packages: ).*", result)
    if match_name is None:
        raise ValueError(
            "Package name could not be extracted from '{}'.".format(request)
        )
    name = match_name.group().strip()

    matched = REQUEST_PATTERN.match(request)
    extra = None if matched is None else matched.group(2)

    return fetch_mapping_from_environ(name, environ_mapping, extra=extra)


def fetch_mapping_from_environ(name, environ_mapping, extra=None):
    """Return a mapping with information about the package *name*.

    :param name: package name
    :param environ_mapping: should be a mapping of environment variables
    :param extra: should be an optional extra requirement label

    :returns: mapping with information about the package gathered from the
        environment. It should be in the form of::

            {
                "identifier": "Foo-0.1.0",
                "name": "Foo",
                "key": "foo",
                "version": "0.1.0",
                "description": "This is a Python package",
                "location": "/path/to/source",
                "target": "Foo/Foo-0.1.0-py27-centos7",
                "python": {
                    "identifier": "2.7",
                    "request": "python >= 2.7, < 2.8"
                },
                "system": {
                    "platform": "linux",
                    "arch": "x86_64",
                    "os": {
                        "name": "centos",
                        "major_version": 7
                    }
                },
                "requirements": [
                    "bim<3,>=2"
                ]
            }

    """
    logger = mlog.Logger(__name__ + ".fetch_mapping_from_environ")

    # Extract package information and its dependency.
    dependency_mapping = extract_dependency_mapping(
        name, environ_mapping, extra=extra
    )

    # Run pip show command to find extra information from extended metadata.
    metadata = qip.command.execute(
        "pip show "
        "--disable-pip-version-check "
        "'{}' -v".format(name),
        environ_mapping,
        quiet=True
    )

    mapping = {
        "identifier": extract_identifier(dependency_mapping["package"]),
        "key": dependency_mapping["package"]["key"],
        "name": dependency_mapping["package"]["package_name"],
        "version": dependency_mapping["package"]["installed_version"],
        "python": fetch_python_request_mapping()
    }

    match_description = re.search("(?<=Summary: ).+", metadata)
    if match_description is not None:
        mapping["description"] = match_description.group().strip()

    match_location = re.search("(?<=Location: ).+", metadata)
    if match_location is not None:
        mapping["location"] = match_location.group().strip()

    if is_system_required(metadata):
        mapping["system"] = qip.system.query()

    command_mapping = extract_command_mapping(metadata)
    if len(command_mapping) > 0:
        mapping["command"] = command_mapping

    if len(dependency_mapping.get("requirements", [])) > 0:
        mapping["requirements"] = dependency_mapping["requirements"]
        logger.debug(
            "Dependencies: {}".format(" ".join(mapping["requirements"]))
        )

    # Add target information to package mapping.
    mapping["target"] = extract_target_path(
        mapping["name"], mapping["identifier"],
        os_mapping=mapping.get("system", {}).get("os")
    )

    logger.info("Fetched '{}'.".format(mapping["identifier"]))
    return mapping


def extract_dependency_mapping(name, environ_mapping, extra=None):
    """Return package mapping for *name* from dependency mapping.

    :param name: package name
    :param environ_mapping: mapping of environment variables
    :param extra: should be an optional extra requirement label

    :returns: None if the package *name* cannot be found in dependency mapping,
        otherwise return dependency mapping. A valid mapping should be in the
        form of::

            {
                "package": {
                    "key": "foo",
                    "package_name": "Foo",
                    "installed_version": "0.1.0",
                },
                "requirements": [
                    "bim<3,>=2"
                ]
            }


    """
    identifier = name.lower()
    if extra is not None:
        identifier += "[{}]".format(extra)

    command = "python {script} {identifier}".format(
        script=PACKAGE_QUERY_SCRIPT,
        identifier=identifier
    )

    result = qip.command.execute(
        command, environ_mapping, quiet=True
    )

    try:
        mapping = json.loads(result)
    except ValueError:
        raise RuntimeError(
            "Impossible to fetch installed package for '{}'".format(identifier)
        )

    return mapping


def extract_identifier(mapping):
    """Return corresponding identifier from package *mapping*.

    :param mapping: package mapping.

        The package mapping must be in the form of::

            {
                "key": "foo",
                "package_name": "Foo",
                "installed_version": "1.11",
            }

    :returns: Corresponding identifier (e.g. "Foo-1.11", "Bar")

    """
    identifier = qip.filesystem.sanitise_value(
        "{name}-{version}".format(
            name=mapping["package_name"],
            version=mapping["installed_version"]
        )
    )

    return identifier


def is_system_required(metadata):
    """Indicate whether package is platform-specific from *metadata*.

    Package `classifiers <https://pypi.org/classifiers/>`_ are retrieved from
    *metadata* to indicate if a specific operating system is required.

    :param metadata: string resulting from the "pip show -v" command.

    :returns: Boolean value

    """
    classifiers = re.findall("Operating System :: .*", metadata)

    # Check if the package is os independent.
    os_independent = (
        len(classifiers) == 1 and
        classifiers[0] == "Operating System :: OS Independent"
    )

    return len(classifiers) > 0 and not os_independent


def extract_command_mapping(metadata):
    """Extract command mapping from entry points within *metadata*.

    :param metadata: string resulting from the "pip show -v" command.

    :returns: mapping in the form of::

        {
            "foo": "python -m foo",
            "bar": "python -m bar"
        }

    """
    mapping = {}

    # Convention: command name can only have alpha-numeric characters, hyphens
    # and points.
    entry_points = re.search(
        r"Entry-points:\n\s*\[console_scripts\]\n((\s*.+\s*=\s*.+\s*\n)+)",
        metadata
    )
    if entry_points is not None:
        entry_points = entry_points.group(1)

        for alias, command in (
            (
                element.split("=")[0].strip(),
                element.split("=")[1].split(":")[0].strip()
            )
            for element in entry_points.split("\n") if element
        ):
            if command.endswith(".__main__"):
                command = command[:-9]

            mapping[alias] = "python -m {}".format(command)

    return mapping


def extract_target_path(name, identifier, os_mapping=None):
    """Return the corresponding target path from package *mapping*.

    :param name: package name
    :param identifier: package identifier
    :param os_mapping: could be a mapping in the form of::

            {
                "name": "centos",
                "major_version": 7
            }

    :returns: Corresponding path (e.g. "Foo/Foo-1.11-py27-centos7")

    """
    path = os.path.join(name, identifier)

    # Indicate Python version
    path += "-py{major}{minor}".format(
        major=sys.version_info.major,
        minor=sys.version_info.minor
    )

    # Indicate system if necessary
    if os_mapping:
        path += "-{os_name}{os_version}".format(
            os_name=os_mapping["name"],
            os_version=os_mapping["major_version"],
        )

    return path


def fetch_python_request_mapping():
    """Return mapping indicating the Python version required.

    :returns: mapping in the form of::

        {
            "identifier": "2.7",
            "request": "python >= 2.7, < 2.8"
        }

    """
    python_version = sys.version_info

    return {
        "identifier": "{major}.{minor}".format(
            major=python_version.major,
            minor=python_version.minor,
        ),
        "request": "python >= {major}.{minor}, < {major}.{next_minor}".format(
            major=python_version.major,
            minor=python_version.minor,
            next_minor=python_version.minor + 1
        )
    }
