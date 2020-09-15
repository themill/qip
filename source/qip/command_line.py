# :coding: utf-8

import os
import sys
import tempfile
import textwrap

import click
import qip
import qip.logging
import wiz
import wiz.config
from qip import __version__

# Initiate logging handler to display potential warning when fetching config.
wiz.logging.configure()

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
    type=click.Choice(qip.logging.levels),
    default="info"
)
def main(**kwargs):
    """Quarantine Installer for Python."""
    qip.logging.configure()
    qip.logging.root.handlers["stderr"].filterer.min = kwargs["verbosity"]


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
        "Update Wiz definition(s) that already exist in the Wiz definitions "
        "output path with additional Python variants."
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
    "-p", "--python",
    help=(
        "Target a specific Python version via a Wiz request or a path to a "
        "Python executable."
    ),
    show_default=True,
    metavar="TARGET",
    default=_CONFIG.get("qip", {}).get("python_target", sys.executable)
)
@click.argument(
    "requests",
    nargs=-1,
    required=True
)
def install(**kwargs):
    """Install one or several packages."""
    logger = qip.logging.Logger(__name__ + ".install")

    output_path = kwargs["output_path"]
    definition_path = kwargs["definition_path"]

    # Fetch definition mapping from definition path if previously extracted
    # definitions should to create new definition.
    definition_mapping = None

    if kwargs["update"]:
        definition_mapping = wiz.fetch_definition_mapping([definition_path])

    qip.install(
        kwargs["requests"], output_path,
        definition_path=definition_path,
        overwrite=kwargs["overwrite_installed"],
        no_dependencies=kwargs["no_dependencies"],
        editable_mode=kwargs["editable"],
        python_target=kwargs["python"],
        definition_mapping=definition_mapping
    )

    logger.info("Package output directory: {!r}".format(output_path))
    logger.info("Definition output directory: {!r}".format(definition_path))
