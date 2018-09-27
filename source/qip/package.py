# :coding: utf-8

from __future__ import print_function
import json

import mlog

import qip.command


def install(requirement, destination, environ_mapping):
    """Install package in *destination* from *requirement*.

    Return a mapping with information about the package, as returned by
    :func:`fetch_package_from_environ`.

    * *requirement* is an instance of
    :class:`packaging.requirements.Requirement`.
    * *destination* should be a valid path in which all packages will be
    installed.
    * *environ_mapping* should be a mapping with all environment variables
    needed.

    """
    logger = mlog.Logger(__name__ + ".install")

    logger.info("Installing {}...".format(requirement))
    qip.command.execute(
        "pip install "
        "--ignore-installed "
        "--no-deps "
        "--prefix {destination} "
        "--no-warn-script-location "
        "--disable-pip-version-check "
        "--no-cache-dir "
        "'{requirement}'".format(
            destination=destination,
            requirement=requirement,
        ),
        environ_mapping
    )

    return fetch_package_from_environ(requirement.name, environ_mapping)


def fetch_package_from_environ(name, environ_mapping):
    """Return package *name* from current environment.

    Return a mapping with information about the package. The mapping should be
    in the form of::

        {
            "package": {
                "identifier": "Foo-0.1.0",
                "key": "foo",
                "package_name": "Foo",
                "installed_version": "0.1.0",
            },
            "dependencies": [
                {
                    "key": "bar",
                    "package_name": "Bar",
                    "installed_version": "0.1.0",
                    "required_version": None
                },
                {
                    "key": "bim",
                    "package_name": "Bim",
                    "installed_version": "2.3.1",
                    "required_version": ">= 2, <3"
                }
            ]
        }

    * *environ_mapping* should be a mapping with all environment variables
    needed.

    """
    logger = mlog.Logger(__name__ + ".fetch_package_from_environ")

    result = qip.command.execute(
        "pipdeptree --json", environ_mapping, quiet=True
    )

    try:
        environment_packages = json.loads(result)
    except ValueError:
        raise RuntimeError(
            "Impossible to fetch tree package for '{}'".format(name)
        )

    mapping = None
    for _mapping in environment_packages:
        _name = _mapping.get("package", {}).get("key")
        if _name == name:
            mapping = _mapping
            break

    if mapping is None:
        raise RuntimeError(
            "Impossible to fetch installed package for '{}'".format(name)
        )

    # Build a unique identifier for the package.
    mapping["package"]["identifier"] = extract_identifier(mapping["package"])

    logger.info("Fetched {}.".format(mapping["package"]["identifier"]))
    return mapping


def extract_identifier(mapping):
    """Return corresponding identifier from package *mapping*.

    *mapping* must be in the form of::

        {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "1.11",
        }

    Corresponding identifier would be "Foo-1.11"

    """
    return qip.filesystem.sanitise_value(
        "{name}-{version}".format(
            name=mapping["package_name"],
            version=mapping["installed_version"]
        )
    )


def extract_request(mapping):
    """Return corresponding requirement request from package *mapping*.

    *mapping* must be in the form of::

        {
            "key": "foo",
            "package_name": "Foo",
            "installed_version": "1.11",
            "required_version": ">=1.5",
        }

    Corresponding request would be "foo >=1.5"

    """
    return "{name} {specifier}".format(
        name=mapping["key"],
        specifier=mapping.get("required_version") or ""
    ).strip()
