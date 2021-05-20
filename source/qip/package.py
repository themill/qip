# :coding: utf-8

import logging
import json
import os
import re

import wiz.filesystem

import qip.command
import qip.environ
import qip.system

#: Compiled regular expression to detect git input.
GIT_PATTERN = re.compile(r"^git@[\w._-]+:")

#: Compiled regular expression to detect request with extra option.
EXTRA_REQUEST_PATTERN = re.compile(r"(?:.*)\s*\[(.+)]")

#: Path to the Python package info script.
PACKAGE_INFO_SCRIPT = os.path.join(
    os.path.dirname(__file__), "package_data", "package_info.py"
)


def install(request, path, context_mapping, cache_path, editable_mode=False):
    """Install package in *path* from *request*.

    :param request: package to be installed. A request can be one of::

            "/path/to/foo/"
            "."
            "foo"
            "foo==0.1.0"
            "foo >= 7, < 8"
            "git@gitlab:rnd/foo.git"
            "git@gitlab:rnd/foo.git@0.1.0"
            "git@gitlab:rnd/foo.git@dev"

    :param path: path to install Python packages to.

    :param context_mapping: contain environment mapping and python mapping, as
        returned from :func:`qip.fetch_context_mapping`.

    :param cache_path: Temporary directory for the pip cache.

    :param editable_mode: install in editable mode. Default is False.

    :raise RuntimeError: if :term:`Pip` fails to install Python package.

    :raise ValueError: if the Python package name can not be extracted from
        *request*.

    :return: mapping with information about the package gathered from the
        environment. It should be in the form of::

            {
                "identifier": "Foo-0.1.0",
                "request": "foo >= 0.1.0, < 1",
                "extra": [],
                "name": "Foo",
                "key": "foo",
                "version": "0.1.0",
                "description": "This is a Python package",
                "location": "/path/to/source",
                "target": "Foo/Foo-0.1.0-py27-centos7",
                "python": {
                    "identifier": "2.7",
                    "request": "python >= 2.7, < 2.8",
                    "library-path": "lib/python2.8/site-packages"
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
    logger = logging.getLogger(__name__ + ".install")

    if GIT_PATTERN.match(request) is not None:
        request = "git+ssh://" + request.replace(":", "/")

    logger.debug("Installing '{}'...".format(request))
    result = qip.command.execute(
        "python -m pip install "
        "--ignore-installed "
        "--no-deps "
        "--prefix {destination} "
        "--no-warn-script-location "
        "--disable-pip-version-check "
        "--cache-dir {cache_dir} "
        "{editable_mode}"
        "'{requirement}'".format(
            editable_mode="-e " if editable_mode else "",
            destination=path,
            requirement=request,
            cache_dir=cache_path
        ),
        context_mapping["environ"]
    )

    match_name = re.search("(?<=Installing collected packages: ).*", result)
    if match_name is None:
        raise ValueError(
            "Package name could not be extracted from '{}'.".format(request)
        )
    name = match_name.group().strip()

    extra_keywords = []

    matched_extra = EXTRA_REQUEST_PATTERN.match(request)
    if matched_extra:
        extra_keywords = matched_extra.group(1).split(",")
        extra_keywords = sorted(key.strip() for key in extra_keywords)
        extra_keywords = [key for key in extra_keywords if len(key)]

    mapping = fetch_mapping_from_environ(
        name, context_mapping,
        extra_keywords=extra_keywords
    )

    mapping["request"] = request
    mapping["extra"] = extra_keywords
    return mapping


def fetch_mapping_from_environ(name, context_mapping, extra_keywords=None):
    """Return a mapping with information about the Python package *name*.

    :param name: Python package name.

    :param context_mapping: contain environment mapping and python mapping, as
        returned from :func:`qip.fetch_context_mapping`.

    :param extra_keywords: List of :term:`extra requirement keywords
        <extras_require>` if required. Default is None.

    :return: mapping with information about the package gathered from the
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
                    "request": "python >= 2.7, < 2.8",
                    "library-path": "lib/python2.8/site-packages"
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
    logger = logging.getLogger(__name__ + ".fetch_mapping_from_environ")

    # Extract package information and its dependency.
    dependency_mapping = extract_dependency_mapping(
        name, context_mapping["environ"],
        extra_keywords=extra_keywords
    )

    # Run pip show command to find extra information from extended metadata.
    metadata = qip.command.execute(
        "python -m pip show "
        "--disable-pip-version-check "
        "'{}' -v".format(name),
        context_mapping["environ"],
        quiet=True
    )

    mapping = {
        "identifier": extract_identifier(
            dependency_mapping["package"],
            extra_keywords=extra_keywords
        ),
        "key": extract_key(
            dependency_mapping["package"],
            extra_keywords=extra_keywords
        ),
        "name": dependency_mapping["package"]["package_name"],
        "module_name": dependency_mapping["package"]["module_name"],
        "version": dependency_mapping["package"]["installed_version"],
        "python": context_mapping["python"]
    }

    match_description = re.search("(?<=Summary: ).+", metadata)
    if match_description is not None:
        mapping["description"] = match_description.group().strip()

    match_location = re.search("(?<=Location: ).+", metadata)
    if match_location is not None:
        mapping["location"] = match_location.group().strip()

    if is_system_required(metadata):
        mapping["system"] = qip.system.query()

    command_mapping = extract_command_mapping(
        metadata, extra_keywords=extra_keywords
    )
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
        context_mapping["python"]["identifier"],
        os_mapping=mapping.get("system", {}).get("os"),
    )

    return mapping


def extract_dependency_mapping(name, environ_mapping, extra_keywords=None):
    """Return mapping for Python package with all dependency requirements.

    :param name: Python package name.

    :param environ_mapping: mapping of environment variables.

    :param extra_keywords: List of :term:`extra requirement keywords
        <extras_require>` if required. Default is None.

    :return: None if the package *name* cannot be found in dependency mapping,
        otherwise return dependency mapping. A valid mapping should be in the
        form of::

            {
                "package": {
                    "key": "foo",
                    "package_name": "Foo",
                    "module_name": "foo"
                    "installed_version": "0.1.0",
                },
                "requirements": [
                    "bim<3,>=2"
                ]
            }

    """
    identifier = name.lower()
    if extra_keywords is not None and len(extra_keywords):
        identifier += "[{}]".format(",".join(extra_keywords))

    command = "python {script} {identifier}".format(
        script=PACKAGE_INFO_SCRIPT,
        identifier=identifier
    )

    result = qip.command.execute(command, environ_mapping, quiet=True)
    try:
        mapping = json.loads(result)
    except ValueError:
        raise RuntimeError(
            "Impossible to fetch installed package for '{}'".format(identifier)
        )

    return mapping


def extract_identifier(mapping, extra_keywords=None):
    """Return corresponding identifier from package *mapping*.

    :param mapping: package mapping. The package mapping must be in the form
        of::

            {
                "key": "foo",
                "package_name": "Foo",
                "installed_version": "1.11",
            }

    :param extra_keywords: List of :term:`extra requirement keywords
        <extras_require>` if required. Default is None.

    :return: Corresponding identifier (e.g. "Foo-1.11", "Bar").

    """
    if extra_keywords is not None and len(extra_keywords):
        extra_keywords = "-" + "-".join(extra_keywords)

    return wiz.filesystem.sanitize_value(
        "{name}{extra}-{version}".format(
            name=mapping["package_name"],
            version=mapping["installed_version"],
            extra=extra_keywords or ""
        )
    )


def extract_key(mapping, extra_keywords=None):
    """Compute key for package *mapping*.

    :param mapping: package mapping. The package mapping must be in the form
        of::

            {
                "key": "foo",
                "package_name": "Foo",
                "installed_version": "1.11",
            }

    :param extra_keywords: List of :term:`extra requirement keywords
        <extras_require>` if required. Default is None.

    :return: Corresponding key (e.g. "foo", "foo-test").

    """
    if extra_keywords is not None and len(extra_keywords):
        extra_keywords = "-" + "-".join(extra_keywords)

    return wiz.filesystem.sanitize_value(
        "{name}{extra}".format(
            name=mapping["key"],
            extra=extra_keywords or ""
        )
    )


def is_system_required(metadata):
    """Indicate whether package is platform-specific from *metadata*.

    Package `classifiers <https://pypi.org/classifiers/>`_ are retrieved from
    *metadata* to indicate if a specific operating system is required.

    :param metadata: string resulting from the `pip show -v
        <https://pip.pypa.io/en/stable/reference/pip_show/>`_ command.

    :return: Boolean value.

    """
    classifiers = re.findall("Operating System :: .*", metadata)

    # Check if the package is os independent.
    os_independent = (
        len(classifiers) == 1 and
        classifiers[0] == "Operating System :: OS Independent"
    )

    return len(classifiers) > 0 and not os_independent


def extract_command_mapping(metadata, extra_keywords=None):
    """Extract command mapping from entry points within *metadata*.

    Package :term:`Entry-Points` are retrieved from *metadata* to extract the
    corresponding commands. Each function defined as ``console_scripts`` will
    be used to create associated command.

    Provided *extra_keywords* are used when commands depend on optional
    dependencies.

    :param metadata: string resulting from the `pip show -v
        <https://pip.pypa.io/en/stable/reference/pip_show/>`_ command.

    :param extra_keywords: List of :term:`extra requirement keywords
        <extras_require>` if required. Default is None.

    :return: command mapping

        It should be in the form of::

            {
                "foo": "python -m foo",
                "bar": "python -m bar.test"
            }

    """
    mapping = {}

    # Convention: command name can only have alpha-numeric characters, hyphens
    # and points.
    entry_points = re.search(
        r"Entry-points:\n\s*\[console_scripts]\n((?:\s*.+\s*=\s*.+\s*\n)+)",
        metadata
    )
    if entry_points is not None:
        entry_points = entry_points.group(1)

        for element in entry_points.split("\n"):
            element = element.strip()
            if not len(element):
                continue

            alias, script = element.split("=")
            alias = alias.strip()
            script = script.strip()

            matched_extra = EXTRA_REQUEST_PATTERN.match(script)
            if matched_extra:
                authorized = set(matched_extra.group(1).split(","))
                if authorized.difference(extra_keywords or []):
                    continue

            command = script.split(":")[0].strip()
            if command.endswith(".__main__"):
                command = command[:-9]

            mapping[alias] = "python -m {}".format(command)

    return mapping


def extract_target_path(name, identifier, python_version, os_mapping=None):
    """Return the corresponding target path from package *mapping*.

    :param name: Python package name.

    :param identifier: Python package identifier.

    :param python_version: Python version identifier (e.g. "2.7").

    :param os_mapping: None or a mapping describing the operating system.
        Default is None.

        It should be in the form of::

            {
                "name": "centos",
                "major_version": 7
            }

    :return: Corresponding path (e.g. "Foo/Foo-1.11-py27-centos7").

    """
    path = os.path.join(name, identifier)

    # Indicate Python version
    path += "-py{}".format(python_version.replace(".", ""))

    # Indicate system if necessary
    if os_mapping:
        path += "-{os_name}{os_version}".format(
            os_name=os_mapping["name"],
            os_version=os_mapping["major_version"],
        )

    return path
