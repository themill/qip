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
    """Qip command line interface."""
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
@click.argument(
    "requests",
    help="Python package(s) to install",
    nargs=-1
)
def install(requests, output, overwrite_installed):
    """Qip install command line interface."""
    qip.install(requests, output, overwrite_installed)
