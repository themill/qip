# :coding: utf-8

import os
import re

import mlog
import wiz

import qip.symbol


def create(mapping, path):
    """Create :term:`Wiz` definition for package *mapping*.

    :param mapping: mapping of the python package built.
    :param path: installation path of all python packages.
    :returns: definition data.

    """
    logger = mlog.Logger(__name__ + ".create")

    definition_data = {
        "identifier": mapping["key"],
        "version": mapping["version"],
        "install-location": path,
        "group": "python"
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

    if "command" in mapping.keys():
        definition_data["command"] = mapping["command"]

    # Compute relative installation path.
    installation_path = os.path.join(
        qip.symbol.INSTALL_LOCATION, mapping["target"]
    )

    # Identify if a library is installed.
    lib_path = os.path.join(
        path, mapping["target"], qip.symbol.P27_LIB_DESTINATION
    )

    if os.path.isdir(lib_path):
        definition_data.setdefault("environ", {})
        definition_data["environ"]["PYTHONPATH"] = (
            "{}:${{PYTHONPATH}}".format(
                os.path.join(installation_path, qip.symbol.P27_LIB_DESTINATION)
            )
        )

    # Identify if an executable is installed.
    bin_path = os.path.join(path, mapping["target"], qip.symbol.BIN_DESTINATION)
    if os.path.isdir(bin_path):
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


def retrieve(mapping, temporary_path, output_path):
    """Retrieve :term:`Wiz` definition from package installed.

    :param mapping: mapping of the python package built.
    :param temporary_path: path where the package was temporarily installed to.
    :param output_path: path where the package was installed to.
    :returns: None if no definition was found, otherwise return the definition.

    """
    logger = mlog.Logger(__name__ + ".retrieve")

    definition_paths = [
        os.path.join(
            temporary_path, "share", "wiz", mapping["name"], "wiz.json"
        )
    ]

    # Necessary as editable mode does not create the 'share' directory.
    if mapping.get("location"):
        definition_paths.append(
            os.path.join(mapping.get("location"), "..", "wiz.json")
        )

    for definition_path in definition_paths:
        if not os.path.exists(definition_path):
            continue

        # Update definitions install locations.
        definition = wiz.load_definition(definition_path)
        definition = _update_install_location(
            definition, output_path, mapping["target"]
        )

        logger.info(
            "Wiz definition extracted from '{}'.".format(mapping["identifier"])
        )
        return definition


def _update_install_location(definition, path, target):
    """Update a definition with new install paths.

    :param definition: valid :class:`~wiz.definition.Definition` instance.
    :param path: path where the package was installed to.
    :param target: relative path to where the package is installed.
    :returns: a definition where all occurances of ${INSTALL_LOCATION} have been
    replaced by ${INSTALL_LOCATION}/target and an 'install-location' key has
    been added.

    """
    target = os.path.join("${INSTALL_LOCATION}", target)

    new_environ = {}
    for key, value in definition.environ.items():
        new_environ[key] = re.sub("\\${INSTALL_LOCATION}", target, value)
    if len(new_environ):
        definition = definition.set("environ", new_environ)

    new_variant = []
    for variant in definition.variants:
        new_environ = {}
        for key, value in variant.environ.items():
            new_environ[key] = re.sub("\\${INSTALL_LOCATION}", target, value)
        if len(new_environ):
            new_variant.append(variant.update("environ", new_environ))
    if len(new_variant):
        definition = definition.set("variants", new_variant)

    return definition.set("install-location", path)
