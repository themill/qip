# :coding: utf-8

from __future__ import print_function
import re
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


def sanitise_request(request):
    """Sanitize *request* if it is a git repository address."""
    if request.startswith("git@gitlab:"):
        return "git+ssh://" + request.replace(":", "/")

    return request


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
                "target": "Foo/Foo-0.1.0-centos7",
                "system": {
                    "platform": "linux",
                    "arch": "x86_64",
                    "os": {
                        "name": "centos",
                        "major_version": 7
                    }
                },
                "requirements": [
                    {
                        "identifier": "Bar-0.1.0",
                        "request": "bar",
                    },
                    {
                        "identifier": "Bim-2.3.1",
                        "request": "bim >= 2, <3",
                    }
                ]
            }

    """
    logger = mlog.Logger(__name__ + ".fetch_package_from_environ")

    dependency_mapping = extract_dependency_mapping(
        name, environ_mapping, extra=extra
    )
    metadata_mapping = extract_metadata_mapping(name, environ_mapping)

    mapping = {
        "identifier": extract_identifier(dependency_mapping["package"]),
        "key": dependency_mapping["package"]["key"],
        "name": dependency_mapping["package"]["package_name"],
        "version": dependency_mapping["package"]["installed_version"],
    }

    mapping.update(metadata_mapping)

    if len(dependency_mapping.get("dependencies", [])) > 0:
        mapping["requirements"] = [
            _dependency_mapping["required_version"]
            for _dependency_mapping in dependency_mapping["dependencies"]
        ]

        logger.debug(
            "Dependencies: {}".format(" ".join(mapping["requirements"]))
        )

    # Add target information to package mapping.
    mapping["target"] = os.path.join(
        mapping["name"], mapping["identifier"]
    )
    if mapping.get("system"):
        os_mapping = mapping["system"]["os"]
        mapping["target"] += "-{}{}".format(
            os_mapping["name"], os_mapping["major_version"]
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
                "dependencies": [
                    {
                        "key": "bar",
                        "package_name": "Bar",
                        "required_version": None
                    },
                    {
                        "key": "bim",
                        "package_name": "Bim",
                        "required_version": ">= 2, <3"
                    }
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


def extract_metadata_mapping(name, environ_mapping):
    """Return package mapping for *name* from available metadata.

    :param name: package name
    :param environ_mapping: mapping of environment variables
    :returns: mapping with information about the package gathered from the
        environment (system and description). It should be in the form of::

            {
                "description": "This is a Python package.",
                "location": "/path/to/source",
                "system": {
                    "platform": "linux",
                    "os": "el >= 6, <7"
                }
            }

    """
    result = qip.command.execute(
        "pip show "
        "--disable-pip-version-check "
        "'{}' -v".format(name),
        environ_mapping,
        quiet=True
    )

    mapping = {}

    match_description = re.search("(?<=Summary: ).+", result)
    if match_description is not None:
        mapping["description"] = match_description.group().strip()

    match_location = re.search("(?<=Location: ).+", result)
    if match_location is not None:
        mapping["location"] = match_location.group().strip()

    # Find out if the package is platform specific from the classifiers
    # (https://pypi.org/classifiers/)
    os_classifiers = re.findall("Operating System :: .*", result)
    if len(os_classifiers) > 0:
        if not (
            len(os_classifiers) == 1 and
            os_classifiers[0] == "Operating System :: OS Independent"
        ):
            mapping["system"] = qip.system.query()

    # Convention: command name can only have alpha-numeric characters, hyphens
    # and points.
    entry_points = re.search(
        r"Entry-points:\n\s*\[console_scripts\]\n((\s*.+\s*=\s*.+\s*\n)+)",
        result
    )
    if entry_points is not None:
        entry_points = entry_points.group(1)

        mapping["command"] = {}
        for alias, command in (
            (
                element.split("=")[0].strip(),
                element.split("=")[1].split(":")[0].strip()
            )
            for element in entry_points.split("\n") if element
        ):
            if command.endswith(".__main__"):
                command = command[:-9]

            mapping["command"][alias] = "python -m {}".format(command)

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

    :returns: Corresponding identifier (ie. "Foo-1.11", "Bar")

    """
    identifier = qip.filesystem.sanitise_value(
        "{name}-{version}".format(
            name=mapping["package_name"],
            version=mapping["installed_version"]
        )
    )

    return identifier
