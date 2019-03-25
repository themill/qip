# :coding: utf-8

import sys
import re
import json
import argparse

try:
    from pip._internal.utils.misc import get_installed_distributions
    from pip._internal.operations.freeze import FrozenRequirement
except ImportError:
    from pip import get_installed_distributions, FrozenRequirement


#: Compiled regular expression to detect request with extra option.
REQUEST_PATTERN = re.compile(r"(.*)\[(\w*)\]")


def display_package(name):
    """Display package mapping from selected *name*.

    Example::

        >>> display_package("foo")

        {
            "package": {
                "installed_version": "1.0.0",
                "key": "foo",
                "package_name": "Foo"
            },
            "requirements": [
                "bim<3,>=2",
                "baz",
            ]
        }


    """
    # Query all installed packages.
    packages = get_installed_distributions(local_only=False)

    # Identify and extract 'extra' label from input *name* if necessary.
    match = REQUEST_PATTERN.match(name)
    labels = []

    if match is not None:
        labels = [match.group(2)]
        name = match.group(1)

    # Compute key from name.
    key = name.lower()

    # Identify selected package within installed packages.
    package = None

    for _package in packages:
        if _package.key == key:
            package = _package
            break

    # Return now if the selected package could not be found in mapping.
    if package is None:
        return

    result = {
        "package": {
            "key": package.key,
            "package_name": package.project_name,
            "installed_version": package.version,
        },
        "requirements": [
            requirement.key + str(requirement.specifier)
            for requirement in package.requires(extras=labels)
        ]
    }

    print(json.dumps(result, sort_keys=True, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pip-query",
        description="Query information about an installed package",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("name", help="Package name to query.")
    namespace = parser.parse_args()

    sys.exit(display_package(namespace.name))
