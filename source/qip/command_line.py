# :coding: utf-8

import os
import click
import mlog
import tempfile

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
def main(verbosity):
    """Quarantine Installer for Python."""
    mlog.configure()
    mlog.root.handlers["stderr"].filterer.filterers[0].min = verbosity


@main.command()
@click.option(
    "-o", "--output-path",
    help="Destination for the package installation data.",
    type=click.Path()
)
@click.option(
    "-d", "--definition-path",
    help=(
        "Destination for the Wiz definitions extracted. No definitions will be "
        "extracted by default."
    ),
    type=click.Path(),
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
    "--no-dependencies",
    help=(
         "Install the specified package(s) without dependencies."
    ),
    is_flag=True,
    default=False
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
    default="python==2.7.*"
)
@click.argument(
    "requests",
    nargs=-1,
    required=True
)
def install(
        requests, output_path, definition_path, overwrite_installed,
        no_dependencies, editable, python
):
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

    if output_path is None:
        output_path = os.path.join(
            tempfile.gettempdir(), "qip", "packages"
        )

    if definition_path is None:
        definition_path = os.path.join(
            tempfile.gettempdir(), "qip", "definitions"
        )

    qip.install(
        requests, output_path,
        definition_path=definition_path,
        overwrite=overwrite_installed,
        no_dependencies=no_dependencies,
        editable_mode=editable,
        python_target=python,
    )

    logger.info("Package output directory: {!r}".format(output_path))
    logger.info("Definition output directory: {!r}".format(definition_path))
