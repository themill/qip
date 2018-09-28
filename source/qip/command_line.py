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
    "-o", "--output",
    help="Destination for the installation",
    type=click.Path(),
    required=True
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
@click.argument("requests", nargs=-1)
def install(requests, output, overwrite_installed, no_dependencies):
    """Install a package.

      Command example::

          qip install sphinx --output .

    """
    qip.install(requests, output, overwrite_installed, no_dependencies)
