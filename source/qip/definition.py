# :coding: utf-8

import os

import mlog
import wiz

import qip.symbol


def create(mapping, output_path, editable_mode=False):
    """Create :term:`Wiz` definition for package *mapping*.

    :param mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.
    :param output_path: installation path of all python packages.
    :param editable_mode: install in editable mode. Default is False.

    :returns: :class:`wiz.definition.Definition` instance.

    """
    logger = mlog.Logger(__name__ + ".create")

    definition_data = {
        "identifier": mapping["key"],
        "version": mapping["version"],
        "namespace": "library"
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
    definition = update_definition(
        definition, mapping, output_path,
        editable_mode=editable_mode
    )

    logger.info(
        "Wiz definition created for '{}'.".format(mapping["identifier"])
    )
    return definition


def retrieve(mapping, temporary_path, output_path, editable_mode=False):
    """Retrieve :term:`Wiz` definition from package installed.

    :param mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.
    :param temporary_path: path where the package was temporarily installed to.
    :param output_path: path where the package was installed to.
    :param editable_mode: install in editable mode. Default is False.

    :returns: None if no definition was found, otherwise return the
        :class:`wiz.definition.Definition` instance.

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
        definition = update_definition(
            definition, mapping, output_path,
            editable_mode=editable_mode
        )

        logger.info(
            "Wiz definition extracted from '{}'.".format(mapping["identifier"])
        )
        return definition


def update_definition(definition, mapping, output_path, editable_mode=False):
    """Update a *definition* from package *mapping*.

    :param definition: :class:`~wiz.definition.Definition` instance.
    :param mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.
    :param output_path: path to the package install root location.
    :param editable_mode: install in editable mode. Default is False.

    """
    if editable_mode:
        definition = definition.set("install-location", mapping["location"])

    else:
        definition = definition.set("install-root", output_path)
        definition = definition.set("install-location", os.path.join(
            qip.symbol.INSTALL_ROOT, mapping["target"],
            qip.symbol.P27_LIB_DESTINATION
        ))

    if "command" in mapping.keys():
        definition = definition.update("command", mapping["command"])

    if "requirements" in mapping.keys():
        definition = definition.extend("requirements", mapping["requirements"])

    return definition
