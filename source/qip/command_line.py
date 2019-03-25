# :coding: utf-8

import os
import click
import mlog
import tempfile

import wiz
import qip
from qip import __version__


@click.group()
@click.version_option(version=__version__)
@click.option(
    "-v", "--verbosity",
    help="Set the logging output verbosity.",
    type=click.Choice(mlog.levels),
    default="info"
)
def main(**kwargs):
    """Quarantine Installer for Python."""
    mlog.configure()
    mlog.root.handlers["stderr"].filterer.filterers[0].min = kwargs["verbosity"]


@main.command()
@click.option(
    "-o", "--output-path",
    help=(
        "Destination for the package installation data. Default will be "
        "'<TEMPORARY_FOLDER>/qip/packages'"
    ),
    type=click.Path(),
    metavar="PATH",
)
@click.option(
    "-d", "--definition-path",
    help=(
        "Destination for the Wiz definitions extracted. Default will be "
        "'<TEMPORARY_FOLDER>/qip/definitions'"
    ),
    type=click.Path(),
    metavar="PATH",
)
@click.option(
    "--update",
    help=(
        "Update Wiz definition(s) that already exist in the Wiz definitions "
        "output path with additional Python variants."
    ),
    is_flag=True,
    default=False
)
@click.option(
    "--no-dependencies",
    help="Install the specified package(s) without dependencies.",
    is_flag=True,
    default=False
)
@click.option(
    "--overwrite-installed/--skip-installed",
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
    default="python==2.7.*",
    show_default=True,
    metavar="TARGET",
)
@click.argument(
    "requests",
    nargs=-1,
    required=True
)
def install(**kwargs):
    """Install a package.

    Command example::

        \b
        qip install .
        qip install /path/to/foo/
        qip install foo
        qip install foo bar
        qip install "foo==0.1.0"
        qip install "foo >= 7, < 8"
        qip install "git@gitlab:rnd/foo.git"
        qip install "git@gitlab:rnd/foo.git@0.1.0"
        qip install "git@gitlab:rnd/foo.git@dev"
        qip install foo -p "python==3.6.*"

    """
    logger = mlog.Logger(__name__ + ".install")

    output_path = kwargs["output_path"]
    definition_path = kwargs["definition_path"]

    if output_path is None:
        output_path = os.path.join(
            tempfile.gettempdir(), "qip", "packages"
        )

    if definition_path is None:
        definition_path = os.path.join(
            tempfile.gettempdir(), "qip", "definitions"
        )

    # Fetch definition mapping from definition path if previously extracted
    # definitions should to create new definition.
    definition_mapping = None

    if kwargs["update"]:
        definition_mapping = wiz.fetch_definition_mapping([definition_path])

    qip.install(
        kwargs["requests"],  output_path,
        definition_path=definition_path,
        overwrite=kwargs["overwrite_installed"],
        no_dependencies=kwargs["no_dependencies"],
        editable_mode=kwargs["editable"],
        python_target=kwargs["python"],
        definition_mapping=definition_mapping
    )

    logger.info("Package output directory: {!r}".format(output_path))
    logger.info("Definition output directory: {!r}".format(definition_path))
