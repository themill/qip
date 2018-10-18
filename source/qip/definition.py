# :coding: utf-8

import os

import mlog
import wiz

import qip.symbol


def create(mapping, path):
    """Create :term:`Wiz` definition for package *mapping*.

    :param mapping: mapping of the python package built
    :param path: path to install the package definition to
    :returns: definition data

    """
    logger = mlog.Logger(__name__ + ".create")

    definition_data = {
        "identifier": mapping["key"],
        "version": mapping["version"]
    }

    if "description" in mapping.keys():
        definition_data["description"] = mapping["description"]

    if "system" in mapping.keys():
        major_version = mapping["system"]["os"]["major_version"]
        definition_data["system"] = {
            "platform": mapping["system"]["platform"],
            "arch": mapping["system"]["arch"],
            "os": (
                "{name} >= {min_version}, < {max_version}".format(
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

    # Compute relative installation path.
    installation_path = os.path.join(
        qip.symbol.INSTALL_LOCATION, mapping["name"], mapping["identifier"]
    )

    if os.path.isdir(os.path.join(path, qip.symbol.P27_LIB_DESTINATION)):
        definition_data.setdefault("environ", {})
        definition_data["environ"]["PYTHONPATH"] = (
            "{}:${{PYTHONPATH}}".format(
                os.path.join(installation_path, qip.symbol.P27_LIB_DESTINATION)
            )
        )

    if os.path.isdir(os.path.join(path, qip.symbol.BIN_DESTINATION)):
        definition_data.setdefault("environ", {})
        definition_data["environ"]["PATH"] = (
            "{}:${{PATH}}".format(
                os.path.join(installation_path, qip.symbol.BIN_DESTINATION)
            )
        )

    logger.info(
        "Wiz definition created for '{}'.".format(mapping["identifier"])
    )
    return definition_data


def retrieve(mapping, path):
    """Retrieve :term:`Wiz` definition from package installed.

    :param mapping: mapping of the python package built
    :param path: path where the package was installed to
    :return: None if no definition was found, otherwise return the definition

    """
    logger = mlog.Logger(__name__ + ".retrieve")

    definition_path = os.path.join(
        path, "share", "wiz", mapping["name"], "wiz.json"
    )
    if not os.path.exists(definition_path):
        return None

    logger.info(
        "Wiz definition extracted from '{}'.".format(mapping["identifier"])
    )
    return wiz.load_definition(definition_path)
