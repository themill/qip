# :coding: utf-8

import click
import mlog

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
    type=click.Path(),
    required=True
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
@click.argument(
    "requests",
    nargs=-1,
    required=True
)
def install(
        requests, output_path, definition_path, overwrite_installed,
        no_dependencies, editable
):
    """Install a package.

      Command example::

          qip install . --output-path .
          qip install /path/to/foo/ --output-path .
          qip install foo --output-path .
          qip install foo bar --output-path .
          qip install "foo==0.1.0" --output-path .
          qip install "foo >= 7, < 8" --output-path .
          qip install "git@gitlab:rnd/foo.git" --output-path .
          qip install "git@gitlab:rnd/foo.git@0.1.0" --output-path .
          qip install "git@gitlab:rnd/foo.git@dev" --output-path .

    """
    qip.install(
        requests, output_path,
        definition_path=definition_path,
        overwrite_packages=overwrite_installed,
        no_dependencies=no_dependencies,
        editable_mode=editable
    )
