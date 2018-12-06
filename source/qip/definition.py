# :coding: utf-8

import os
import re

import mlog
import wiz

import qip.symbol


def create(mapping, output_path, editable_mode):
    """Create :term:`Wiz` definition for package *mapping*.

    :param mapping: mapping of the python package built.
    :param output_path: installation path of all python packages.
    :param editable_mode: install in editable mode. Default is False.

    :returns: definition data.

    """
    logger = mlog.Logger(__name__ + ".create")

    definition_data = {
        "identifier": mapping["key"],
        "version": mapping["version"],
        "install-location": output_path,
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

    # Identify if a library is installed.
    lib_path = os.path.join(
        output_path, mapping["target"], qip.symbol.P27_LIB_DESTINATION
    )
    if os.path.isdir(lib_path):
        definition_data.setdefault("environ", {})
        definition_data["environ"]["PYTHONPATH"] = (
            "{}:${{PYTHONPATH}}".format(qip.symbol.INSTALL_LOCATION)
        )

    # Update definition with install-location, commands and requirements.
    definition = wiz.definition.Definition(definition_data)
    definition = _update_install_location(
        definition, output_path, mapping, editable_mode
    )
    definition = _update_command(definition, mapping)
    definition = _update_requirements(definition, mapping)

    logger.info(
        "Wiz definition created for '{}'.".format(mapping["identifier"])
    )
    return definition


def retrieve(mapping, temporary_path, output_path, editable_mode):
    """Retrieve :term:`Wiz` definition from package installed.

    :param mapping: mapping of the python package built.
    :param temporary_path: path where the package was temporarily installed to.
    :param output_path: path where the package was installed to.
    :param editable_mode: install in editable mode. Default is False.

    :returns: None if no definition was found, otherwise return the definition.

    """
    logger = mlog.Logger(__name__ + ".retrieve")

    definition_paths = [os.path.join(
        temporary_path, "share", "wiz", mapping["name"], "wiz.json"
    )]

    # Necessary as editable mode does not create the 'share' directory.
    if mapping.get("location"):
        definition_paths.append(
            os.path.join(mapping.get("location"), "..", "wiz.json")
        )

    for definition_path in definition_paths:
        if not os.path.exists(definition_path):
            continue

        # Update definition with install-location, commands and requirements.
        definition = wiz.load_definition(definition_path)
        definition = _update_install_location(
            definition, output_path, mapping, editable_mode
        )
        definition = _update_command(definition, mapping)
        definition = _update_requirements(definition, mapping)

        # Append INSTALL_LOCATION to potentially existing PYTHONPATH
        pythonpath = [
            path for path
            in definition.get("environ", {}).get("PYTHONPATH", "").split(os.pathsep)
            if path not in ["", "${PYTHONPATH}", "$PYTHONPATH"]
        ]
        pythonpath.append(qip.symbol.INSTALL_LOCATION)
        definition = definition.update("environ", {
            "PYTHONPATH": "{}:${{PYTHONPATH}}".format(os.pathsep.join(pythonpath))
        })

        logger.info(
            "Wiz definition extracted from '{}'.".format(mapping["identifier"])
        )
        return definition


def _update_install_location(definition, path, mapping, editable_mode):
    """Update a definition with new install paths.

    :param definition: valid :class:`~wiz.definition.Definition` instance.
    :param path: path to the package install root location.
    :param mapping: mapping of the python package built.
    :param editable_mode: install in editable mode. Default is False.

    :returns: a definition where all "install-location" has been set to the
    source when in *editable mode*, otherwise "install-root" is set to the
    output *path* and "install-location" is set to a relative path targetting
    the site-package install of the package.

    """
    if editable_mode:
        definition = definition.set("install-location", mapping["location"])
    else:
        definition = definition.set("install-root", path)
        definition = definition.set("install-location", os.path.join(
            qip.symbol.INSTALL_ROOT, mapping["target"],
            qip.symbol.P27_LIB_DESTINATION
        ))

    return definition


def _update_command(definition, mapping):
    """Update a definition with new commands.

    :param definition: valid :class:`~wiz.definition.Definition` instance.
    :param mapping: mapping of the python package built.

    :returns: a definition where the command mapping has been updated with
    commands retrieved from the package.

    """
    if "command" in mapping.keys():
        definition = definition.update("command", mapping["command"])
    return definition


def _update_requirements(definition, mapping):
    """Update a definition with new requirements.

    :param definition: valid :class:`~wiz.definition.Definition` instance.
    :param mapping: mapping of the python package built.

    :returns: a definition where the requirements list has been extended with
    requirements retrieved from the package.

    """
    if "requirements" in mapping.keys():
        definition = definition.extend("requirements", [
            _mapping["request"] for _mapping in mapping["requirements"]
        ])
    return definition