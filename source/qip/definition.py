# :coding: utf-8

import os

import mlog
import wiz
import wiz.utility

import qip.environ
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
        "description": mapping["description"],
        "namespace": "library",
        "variants": [
            {
                "identifier": mapping["python"]["identifier"],
                "environ": {
                    "PYTHONPATH": "{}:${{PYTHONPATH}}".format(
                        qip.symbol.INSTALL_LOCATION
                    )
                },
                "requirements": (
                    [mapping["python"]["request"]] +
                    mapping.get("requirements", [])
                )
            }
        ]
    }

    # Add commands mapping.
    if "command" in mapping.keys():
        definition_data["command"] = mapping["command"]

    # Add system constraint if necessary.
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

    # Target package location if the installation is in editable mode.
    if editable_mode:
        definition_data["variants"][0]["install-location"] = mapping["location"]

    else:
        definition_data["install-root"] = output_path
        definition_data["variants"][0]["install-location"] = os.path.join(
            qip.symbol.INSTALL_ROOT, mapping["target"],
            qip.environ.python_library_path()
        )

    definition = wiz.definition.Definition(definition_data)
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
            os.path.abspath(
                os.path.join(mapping.get("location"), "..", "wiz.json")
            )
        )

    for definition_path in definition_paths:
        if not os.path.exists(definition_path):
            continue

        # Update definition with install-location, commands and requirements.
        definition = wiz.load_definition(definition_path)

        # Add commands to the root level.
        if "command" in mapping.keys():
            definition = definition.update("command", mapping["command"])

        # Target package location if the installation is in editable mode.
        location_path = mapping.get("location", "")

        if not editable_mode:
            definition = definition.set("install-root", output_path)
            location_path = os.path.join(
                qip.symbol.INSTALL_ROOT, mapping["target"],
                qip.environ.python_library_path()
            )

        # Process all requirements to detect duplication.
        python_request = mapping["python"]["request"]

        requirements = [
            wiz.utility.get_requirement(_req)
            for _req in [python_request] + mapping.get("requirements", [])
        ]

        _definition = _update_variant(
            definition, mapping["python"]["identifier"], requirements,
            location_path
        )

        if not _definition:
            _definition = definition.extend("variants", [{
                "identifier": mapping["python"]["identifier"],
                "install-location": location_path,
                "requirements": requirements
            }])

        logger.info(
            "Wiz definition extracted from '{}'.".format(mapping["identifier"])
        )
        return _definition


def _update_variant(definition, identifier, requirements, location_path):
    """Update *definition* variant corresponding to *identifier*.

    Return updated :class:`wiz.definition.Definition` instance or None.

    :param definition: :class:`wiz.definition.Definition` instance
    :param identifier: variant identifier
    :param requirements: list of Requirement instances
    :param location_path: path to package.

    :returns: Boolean value

    """
    for index, variant in enumerate(definition.variants):
        if variant.identifier != identifier:
            continue

        variant = variant.set("install-location", location_path)

        # Add requirements that are not already in the definition.
        remaining = set(requirements).difference(variant.requirements)
        variant = variant.extend(
            "requirements",
            [_req for _req in requirements if _req in remaining]
        )

        definition = definition.remove_index("variants", index)
        return definition.insert("variants", variant, index)
