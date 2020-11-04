# :coding: utf-8

import logging
import os
import sys
import tempfile
import textwrap

import click
import wiz
import wiz.config

import qip
import qip._logging
from qip import __version__

# Initiate logging handler to display potential warning when fetching config.
qip._logging.initiate()

#: Retrieve configuration mapping to initialize default values.
_CONFIG = wiz.config.fetch()

#: Click default context for all commands.
CONTEXT_SETTINGS = dict(
    max_content_width=90,
    help_option_names=["-h", "--help"],
)


@click.group(
    context_settings=CONTEXT_SETTINGS
)
@click.version_option(version=__version__)
@click.option(
    "-v", "--verbosity",
    help="Set the logging output verbosity.",
    type=click.Choice(qip._logging.LEVEL_MAPPING.keys()),
    default="info"
)
def main(**kwargs):
    """Quarantine Installer for Python."""
    qip._logging.initiate(console_level=kwargs["verbosity"])


@main.command(
    name="install",
    help=textwrap.dedent(
        """
        Install one or several packages.
    
        Command example:

        \b
        >>> qip install .
        >>> qip install /path/to/foo/
        >>> qip install foo
        >>> qip install foo bar
        >>> qip install "foo==0.1.0"
        >>> qip install "foo >= 7, < 8"
        >>> qip install "git@gitlab:rnd/foo.git"
        >>> qip install "git@gitlab:rnd/foo.git@0.1.0"
        >>> qip install "git@gitlab:rnd/foo.git@dev"
        >>> qip install foo -p "python==3.6.*"
        """
    ),
    short_help="Install one or several packages.",
    context_settings=CONTEXT_SETTINGS
)
@click.option(
    "-o", "--output-path",
    help=(
        "Destination for the package installation data. Default is "
        "'<TEMPORARY_FOLDER>/qip/packages'"
    ),
    type=click.Path(),
    metavar="PATH",
    default=(
        _CONFIG.get("qip", {}).get(
            "packages_output", os.path.join(
                tempfile.gettempdir(), "qip", "packages"
            )
        )
    ),
)
@click.option(
    "-d", "--definition-path",
    help=(
        "Destination for the Wiz definitions extracted. Default is "
        "'<TEMPORARY_FOLDER>/qip/definitions'"
    ),
    type=click.Path(),
    metavar="PATH",
    default=(
        _CONFIG.get("qip", {}).get(
            "definitions_output", os.path.join(
                tempfile.gettempdir(), "qip", "definitions"
            )
        )
    ),
)
@click.option(
    "-u", "--update",
    help=(
        "Include additional variants from existing Wiz definitions, using "
        "definitions previously exported in the same definitions output path."
    ),
    is_flag=True,
    default=False
)
@click.option(
    "-N", "--no-dependencies",
    help="Install the specified package(s) without dependencies.",
    is_flag=True,
    default=False
)
@click.option(
    "-f/-s", "--overwrite-installed/--skip-installed",
    help=(
        "Indicate whether packages already installed should be overwritten "
        "or skipped. By default, a user confirmation will be required."
    ),
    default=None
)
@click.option(
    "-e", "--editable",
    help=(
        "Install a project in editable mode (i.e. setuptools \"develop mode\") "
        "from a local project path or a VCS url."
    ),
    is_flag=True,
    default=False
)
@click.option(
    "-I", "--ignore-registries",
    help=(
         "Ignore Wiz registries when determining whether a package "
         "should be skipped or updated."
    ),
    is_flag=True,
    default=False
)
@click.option(
    "-p", "--python",
    help=(
        "Target a specific Python version via a Wiz request or a path to a "
        "Python executable."
    ),
    show_default=True,
    metavar="TARGET",
    default=_CONFIG.get("qip", {}).get("python_target", sys.executable)
)
@click.option(
    "-R", "--continue-on-error",
    help="Continue installation process when a package fails to install.",
    is_flag=True,
    default=False
)
@click.argument(
    "requests",
    nargs=-1,
    required=True
)
def install(**kwargs):
    """Install one or several packages."""
    logger = logging.getLogger(__name__ + ".install")

    output_path = kwargs["output_path"]
    definition_path = kwargs["definition_path"]

    registry_paths = []

    if not kwargs["ignore_registries"]:
        registry_paths += wiz.registry.get_defaults()

    if kwargs["update"]:
        registry_paths += [definition_path]

    try:
        success = qip.install(
            kwargs["requests"], output_path,
            definition_path=definition_path,
            overwrite=kwargs["overwrite_installed"],
            no_dependencies=kwargs["no_dependencies"],
            editable_mode=kwargs["editable"],
            python_target=kwargs["python"],
            registry_paths=registry_paths,
            update_existing_definitions=kwargs["update"],
            continue_on_error=kwargs["continue_on_error"],
        )
    except RuntimeError as error:
        raise click.exceptions.ClickException(
            "Impossible to resume installation process:\n\n{}".format(error)
        )

    if not success:
        raise click.exceptions.ClickException("No packages installed.")

    logger.info("Package output directory: {!r}".format(output_path))
    logger.info("Definition output directory: {!r}".format(definition_path))
