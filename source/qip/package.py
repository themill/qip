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
        packages = json.loads(result)
    except ValueError:
        raise RuntimeError(
            "Impossible to fetch tree package for '{}'".format(name)
        )

    package = None
    for _package in packages:
        _name = _package.get("package", {}).get("key")
        if _name == name:
            package = _package
            break

    if package is None:
        raise RuntimeError(
            "Impossible to fetch installed package for '{}'".format(name)
        )

    logger.info(
        "Fetched {name}-{version}.".format(
            name=package["package"]["package_name"],
            version=package["package"]["installed_version"],
        )
    )
    return package

