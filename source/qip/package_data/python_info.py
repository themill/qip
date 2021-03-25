# :coding: utf-8

import argparse
import json
import os
import sys


def display_python_mapping():
    """Display Python version information mapping.

    The information is displayed as a :term:`JSON` encoded mapping so that it
    can easily be retrieved via a subprocess.

    :return: None

    Example::

        >>> display_python_mapping()

        {
            "identifier": "2.7",
            "request": "python >= 2.7, < 2.8",
            "library-path": "lib/python2.7/site-packages"
        }


    """
    python_version = sys.version_info

    name = "python{major}.{minor}".format(
        major=sys.version_info.major,
        minor=sys.version_info.minor,
    )

    mapping = {
        "identifier": "{major}.{minor}".format(
            major=python_version.major,
            minor=python_version.minor,
        ),
        "request": "python >= {major}.{minor}, < {major}.{next_minor}".format(
            major=python_version.major,
            minor=python_version.minor,
            next_minor=python_version.minor + 1
        ),
        "library-path": os.path.join("lib", name, "site-packages")
    }

    print(json.dumps(mapping, sort_keys=True, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python-info",
        description="Query information about a Python environment",
    )
    namespace = parser.parse_args()

    sys.exit(display_python_mapping())
