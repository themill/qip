# :coding: utf-8

import argparse
import json
import re
import sys

import pkg_resources

#: Compiled regular expression to detect request with extra option.
REQUEST_PATTERN = re.compile(r"(.*)\[(\w*)]")

#: Metadata file containing the top-level Python module name.
TOP_LEVEL_METADATA_FILE = "top_level.txt"


def display_package_mapping(name):
    """Display Python package information mapping from selected *name*.

    :term:`Pip` Python API is being used to fetch useful information about a
    package within an environment. The information is displayed as a
    :term:`JSON` encoded mapping so that it can easily be retrieved via a
    subprocess.

    :param name: Python package name.

    :return: None

    Example::

        >>> display_package_mapping("foo")

        {
            "package": {
                "installed_version": "1.0.0",
                "key": "foo",
                "package_name": "Foo",
                "module_name": "foo"
            },
            "requirements": [
                "bim<3,>=2",
                "baz",
            ]
        }


    """
    # Identify and extract 'extra' label from input *name* if necessary.
    match = REQUEST_PATTERN.match(name)
    labels = []

    if match is not None:
        labels = [match.group(2)]
        name = match.group(1)

    # Identify selected package.
    package = pkg_resources.get_distribution(name.lower())

    # Module name should be fetched from the metadata, but we will use the
    # package name if we cannot access the top_level.txt file.
    module_name = package.project_name
    if package.has_metadata(TOP_LEVEL_METADATA_FILE):
        module_name = package.get_metadata(TOP_LEVEL_METADATA_FILE).strip()

    result = {
        "package": {
            "key": package.key,
            "package_name": package.project_name,
            "module_name": module_name,
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
        prog="package-info",
        description="Query information about an installed Python package",
    )
    parser.add_argument("name", help="Python package name to query.")
    namespace = parser.parse_args()

    sys.exit(display_package_mapping(namespace.name))
