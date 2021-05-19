# :coding: utf-8

import logging
import functools
import os

import wiz
import wiz.definition
import wiz.environ
import wiz.exception
import wiz.symbol
import wiz.utility

#: Common namespace for all :term:`Wiz` definition.
NAMESPACE = "library"


def export(
    path, package_mapping, output_path, editable_mode=False,
    custom_definition=None, existing_definition=None
):
    """Export :term:`Wiz` definition to *path* for package mapping.

    :param path: destination path for the :term:`Wiz` definition.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :param output_path: root destination path for Python packages installation.

    :param editable_mode: indicate whether the Python package location should
        target the source installation package. Default is False.

    :param custom_definition: :class:`wiz.definition.Definition` instance to
        update as returned by :func:`fetch_custom`. Default is None, which means
        that a default definition will be created from package mapping only.

    :param existing_definition: :class:`wiz.definition.Definition` instance to
        extract additional variants from as returned by :func:`fetch_existing`.
        Default is None which means that no additional variants will be added to
        new definition exported.

    """
    # Extract additional variants from existing definition if possible.
    additional_variants = None
    if existing_definition is not None:
        additional_variants = [
            variant.data() for variant in existing_definition.variants
        ]

    # Update definition or create a new definition.
    if custom_definition is not None:
        definition = update(
            custom_definition, package_mapping, output_path,
            editable_mode=editable_mode,
            additional_variants=additional_variants,
        )

    else:
        definition = create(
            package_mapping, output_path,
            editable_mode=editable_mode,
            additional_variants=additional_variants
        )

    wiz.export_definition(path, definition, overwrite=True)


def fetch_custom(package_mapping):
    """Retrieve :term:`Wiz` definition from package mapping installed.

    Return the :term:`Wiz` definition extracted from a
    :file:`package_data/wiz.json` file found within the package installation
    path.

    If :term:`extra requirement keywords <extras_require>` are called,
    :term:`Wiz` definition containing each keyword will also be fetched and
    merged together into one definition.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :raise wiz.exception.WizError: if the :term:`Wiz` definition found is
        incorrect.

    :return: :class:`wiz.definition.Definition` instance fetched, or None if
        no definition was found.

    .. seealso:: :ref:`development/custom_definition`

    """
    logger = logging.getLogger(__name__ + ".fetch_custom")

    definitions = []

    for key in [None] + package_mapping["extra"]:
        name = "wiz.json" if not key else "wiz-{}.json".format(key)
        path = os.path.join(
            package_mapping["location"], package_mapping["module_name"],
            "package_data", name
        )

        if os.path.exists(path):
            definition = wiz.definition.load(path, mapping={
                "identifier": package_mapping["key"],
                "version": package_mapping["version"]
            })
            definitions.append(definition)

    if len(definitions):
        definition = definitions[0]
        data = definition.data(copy_data=False)

        # Update first definition with data fetched from other definitions.
        for _definition in definitions[1:]:
            wiz.utility.deep_update(data, _definition.data(copy_data=False))

        logger.info(
            "\tWiz definition extracted from '{}'.".format(
                package_mapping["identifier"]
            )
        )
        return definition


def fetch_existing(package_mapping, definition_mapping, namespace=None):
    """Retrieve corresponding :term:`Wiz` definition in definition mapping.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :param definition_mapping: mapping regrouping all available definitions as
        returned by :func:`wiz.fetch_definition_mapping`.

    :param namespace: Namespace of the definition to fetch. Default is
        :data:`NAMESPACE`.

    :return: :class:`wiz.definition.Definition` instance fetched, or None if
        no definition was found.

    """
    namespace = namespace or NAMESPACE

    try:
        return wiz.fetch_definition(
            "{0}::{1[key]}=={1[version]}".format(namespace, package_mapping),
            definition_mapping
        )
    except wiz.exception.RequestNotFound:
        pass


def create(
    package_mapping, output_path, editable_mode=False, additional_variants=None
):
    """Create :term:`Wiz` definition from package mapping.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :param output_path: root destination path for Python packages installation.

    :param editable_mode: indicate whether the Python package location should
        target the source installation package. Default is False.

    :param additional_variants: None or list of variant mappings that should be
        added to the definition created. Default is None.

    :return: :class:`wiz.definition.Definition` instance created.

    """
    logger = logging.getLogger(__name__ + ".create")

    definition_data = {
        "identifier": package_mapping["key"],
        "version": package_mapping["version"],
        "description": package_mapping["description"],
        "namespace": NAMESPACE,
        "environ": {
            "PYTHONPATH": "${{{}}}:${{PYTHONPATH}}".format(
                wiz.symbol.INSTALL_LOCATION
            )
        }
    }

    # Add commands mapping.
    if "command" in package_mapping.keys():
        definition_data["command"] = package_mapping["command"]

    # Add system constraint if necessary.
    if "system" in package_mapping.keys():
        definition_data["system"] = _process_system_mapping(package_mapping)

    # Target package location if the installation is in editable mode.
    location_path = package_mapping.get("location", "")

    if not editable_mode:
        definition_data["install-root"] = output_path
        location_path = os.path.join(
            "${{{}}}".format(wiz.symbol.INSTALL_ROOT),
            package_mapping["target"],
            package_mapping["python"]["library-path"]
        )

    # Update and set variant for python version.
    variants = []

    if additional_variants is not None:
        variants = sorted(
            additional_variants,
            key=functools.cmp_to_key(_compare_variants)
        )

    _update_variants(variants, package_mapping, location_path)

    definition_data["variants"] = variants

    definition = wiz.definition.Definition(definition_data)
    logger.info(
        "\tWiz definition created for '{0[identifier]}'.".format(
            package_mapping
        )
    )
    return definition


def update(
    definition, package_mapping, output_path, editable_mode=False,
    additional_variants=None
):
    """Update *definition* from package mapping.

    :param definition: :class:`wiz.definition.Definition` instance as returned
        by :func:`fetch_custom`.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :param output_path: root destination path for Python packages installation.

    :param editable_mode: indicate whether the Python package location should
        target the source installation package. Default is False.

    :param additional_variants: None or list of variant mappings that should be
        added to the definition updated. Default is None.

    :return: Updated :class:`wiz.definition.Definition` instance.

    """
    if not definition.description:
        definition = definition.set(
            "description", package_mapping["description"]
        )

    if not definition.version:
        definition = definition.set("version", package_mapping["version"])

    if not definition.namespace:
        definition = definition.set("namespace", NAMESPACE)

    if not definition.system and package_mapping.get("system"):
        definition = definition.set(
            "system", _process_system_mapping(package_mapping)
        )

    if package_mapping.get("command"):
        definition = definition.update("command", package_mapping["command"])

    # Update environ mapping
    environ_mapping = {
        "PYTHONPATH": "${{{}}}:${{PYTHONPATH}}".format(
            wiz.symbol.INSTALL_LOCATION
        )
    }

    python_path = definition.environ.get("PYTHONPATH")
    if python_path:
        environ_mapping["PYTHONPATH"] = wiz.environ.substitute(
            environ_mapping["PYTHONPATH"], {"PYTHONPATH": python_path}
        )

    definition = definition.update("environ", environ_mapping)

    # Target package location if the installation is in editable mode.
    package_path = package_mapping.get("location", "")

    if not editable_mode:
        definition = definition.set("install-root", output_path)
        package_path = os.path.join(
            "${{{}}}".format(wiz.symbol.INSTALL_ROOT),
            package_mapping["target"],
            package_mapping["python"]["library-path"]
        )

    # Merge additional variants with existing variants.
    variants = _merge_variants(definition, additional_variants)

    # Update variants with information from package.
    _update_variants(variants, package_mapping, package_path)

    return definition.set("variants", variants)


def _merge_variants(definition, additional_variants=None):
    """Return merged list of variants and definition variants.

    Variants from *definition* have priority over additional variants.

    :param definition: :class:`wiz.definition.Definition` instance as returned
        by :func:`fetch_custom`.

    :param additional_variants: None or list of variant mappings that should be
        added to the definition updated. Default is None.

    :return: list of sorted merged variant mappings.

    """
    mapping = {v["identifier"]: v for v in additional_variants or []}

    for variant in definition.variants:
        identifier = variant.identifier

        if identifier in mapping:
            wiz.utility.deep_update(mapping[identifier], variant.data())
        else:
            mapping[identifier] = variant.data()

    return sorted(mapping.values(), key=functools.cmp_to_key(_compare_variants))


def _update_variants(variants, package_mapping, path):
    """Add variant corresponding to *identifier* to the *variant* list.

    Update existing variant if necessary or add new variant corresponding to the
    python version required. If a new variant is added, it will be inserted
    to the variant list so that the highest Python version is always first.

    :param variants: list of variant mappings to update.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :param path: path where python package has been installed.

    :return: None.

    .. note::

        The *variants* list will be mutated.

    """
    identifier = package_mapping["python"]["identifier"]
    python_request = package_mapping["python"]["request"]

    # Process all requirements to detect duplication.
    requirements = _process_requirements(package_mapping, python_request)

    # Index of new variant if necessary.
    _index = 0

    for index, variant in enumerate(variants):
        if variant["identifier"] != identifier:

            # Update index for new variant.
            if _compare_variants({"identifier": identifier}, variant) > 0:
                _index = index + 1

            continue

        variant["install-location"] = path

        # Add requirements that are not already in the definition.
        variant.setdefault("requirements", [])
        variant["requirements"] += [
            req for req in requirements
            if not any(
                req.replace(" ", "") == _req.replace(" ", "")
                for _req in variant["requirements"]
            )
        ]

        del variants[index]
        variants.insert(index, variant)
        return

    # If no variant has been updated, create a new variant.
    variant = {
        "identifier": identifier,
        "install-location": path,
        "requirements": requirements
    }

    variants.insert(_index, variant)


def _compare_variants(variant1, variant2):
    """Compare identifier values from variant mappings.

    Both identifiers will be converted into a negative float if possible (e.g.
    "2.7" will become -2.7). If one or both identifiers cannot be converted, the
    string value  is kept.

    If both identifiers are of the same type:

    * Return -1 if *identifier2* if higher than *identifier1*.
    * Return 1 if *identifier1* if higher than *identifier2*.
    * Return 0 if *identifier1* if higher than *identifier2*.

    If only *identifier1* is converted into a negative float, -1 is returned.

    If only *identifier2* is converted into a negative float, 1 is returned.

    :param variant1: Variant reference mapping.

    :param variant2: Variant reference mapping to compare *variant1* with.

    :return: Numerical value following the rules above (-1, 1 or 0).

    """
    try:
        identifier1 = -float(variant1["identifier"])
    except ValueError:
        identifier1 = variant1["identifier"]

    try:
        identifier2 = -float(variant2["identifier"])
    except ValueError:
        identifier2 = variant2["identifier"]

    if type(identifier1) == type(identifier2):
        if identifier1 == identifier2:
            return 0
        return -1 if identifier1 < identifier2 else 1

    elif isinstance(identifier1, float):
        return -1
    return 1


def _process_system_mapping(package_mapping):
    """Compute 'system' keyword for the :term:`Wiz` definition from mapping.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :return: system mapping.

    """
    major_version = package_mapping["system"]["os"]["major_version"]
    return {
        "platform": package_mapping["system"]["platform"],
        "arch": package_mapping["system"]["arch"],
        "os": (
            "{name} >= {min_version}, < {max_version}".format(
                name=package_mapping["system"]["os"]["name"],
                min_version=major_version,
                max_version=major_version + 1,
            )
        )
    }


def _process_requirements(package_mapping, python_request):
    """Compute 'requirements' keyword for the :term:`Wiz` definition.

    :param package_mapping: mapping of the python package built as returned by
        :func:`qip.package.install`.

    :param python_request: Python version requirement (e.g.
        "python >=2.7, <2.8")

    :return: requirements list.

    """
    requests = [python_request]

    # Add the library namespace for all requirements fetched.
    for request in package_mapping.get("requirements", []):
        request = "{}::{}".format(NAMESPACE, request)
        requirement = wiz.utility.get_requirement(request)
        requirement.extras = {package_mapping["python"]["identifier"]}
        requests.append(str(requirement))

    return requests
