# :coding: utf-8

import os
import json

import wiz

import qip.command
import qip.logging


#: Path to the python info script.
_PYTHON_INFO_SCRIPT = os.path.join(
    os.path.dirname(__file__), "package_data", "python_info.py"
)


def fetch(python_target, mapping=None):
    """Fetch mapping with all environment variables required.

    :param python_target: Target a specific Python version via a Wiz request or
        a path to a Python executable (e.g. "python==2.7.*" or
        "/path/to/bin/python").

    :param mapping: optional custom environment mapping to be added to initial
        environment.

    :return: environment mapping

        It should be in the form of::

            {
                "PATH": "/path/to/bin",
                "PYTHONPATH": "/path/to/lib/site-packages",
            }

    Example::

        >>> fetch("python==2.7.*")
        >>> fetch("/path/to/bin/python")

    """
    logger = qip.logging.Logger(__name__ + ".fetch")
    logger.debug("initial environment: {}".format(mapping))

    if mapping is None:
        mapping = {}

    # If a Python executable is provided, use it instead of the Wiz request.
    if os.path.isfile(python_target) or os.sep in python_target:
        environ_mapping = mapping.copy()
        environ_mapping.update({
            "PATH": "{}:${{PATH}}".format(os.path.dirname(python_target))
        })
        context = {"environ": environ_mapping}

    else:
        context = wiz.resolve_context([python_target], environ_mapping=mapping)

    return context["environ"]


def fetch_python_mapping(environ_mapping):
    """Fetch Python version mapping.

    :param environ_mapping: mapping of environment variables

    :return: python mapping.

        It should be in the form of::

            {
                "identifier": "2.7",
                "request": "python >= 2.7, < 2.8",
                "installation-target": "lib/python2.7/site-packages"
            }

    """
    result = qip.command.execute(
        "python {}".format(_PYTHON_INFO_SCRIPT), environ_mapping, quiet=True
    )
    try:
        mapping = json.loads(result)
    except ValueError:
        raise RuntimeError(
            "Impossible to fetch Python version mapping'"
        )

    return mapping
