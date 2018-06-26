# :coding: utf-8
import click
import subprocess
import _version as ver
import re
import os
import sys
import json

import config
from printer import Printer
from distutils.dir_util import copy_tree
from remotecmd import CmdRunner
from qipcore import Qip

cfg = config.Config()
cfg.from_pyfile("configs/base.py")
cfg.from_envvar("QIP_CONFIG", silent=True)


class QipContext(object):
    logger = None
    target_conf_dict = {}
    qip_config = {}


@click.group()
@click.pass_context
@click.version_option(version=ver.__version__)
@click.option("-v", '--verbose', count=True)
@click.option("-y", is_flag=True, help="Yes to all prompts")
def qipcmd(ctx, verbose, y):
    """Install or download Python packages to an isolated location."""
    qctx = QipContext()
    qctx.printer = Printer(verbose)
    verbose += 1
    qctx.target = None
    qctx.yestoall = y
    ctx.obj = qctx


def set_git_ssh(package):
    """
    Replace the gitlab copied prefix with the one for pip
    """
    if package.startswith("git@gitlab:"):
        package = 'git+ssh://' + package.replace(':', '/')
    return package


def has_git_version(package):
    """
    Regex to test if a gitlab URL has a version specified
    """
    m = re.search(r'\.git@.+$', package)
    if m is None:
        return False
    return True


def write_deps_to_file(name, specs, deps, filename):
    """
    Dump a json representation of the *deps* and *specs* to *filename*
    Should be used during testing only
    """
    try:
        os.path.mkdirs(os.path.basename(filename))
    except:
        pass

    with open(filename, 'w') as fh:
        json.dump(deps, fh)


def read_deps_from_file(name, specs, filename):
    """
    Read the deps from *filename* for the given package *name* and *specs*
    Should be using during testing only
    """
    with open(filename, 'r') as fh:
        deps = json.load(fh)
    return deps


@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--nodeps', '-n', is_flag=True, help='Install the specified package without deps')
@click.option('--download', '-d', is_flag=True, help='Download packages without prompting')
@click.option('--depfile', default="", help='Use json file to get deps')
@click.option('--target', '-t', prompt="Target to install to", default='centos72',
              type=click.Choice(cfg['TARGETS'].keys()))
@click.option('--password', prompt="Your password [leave blank if using ssh keys]",
              default="", hide_input=True)
def install(ctx, **kwargs):
    """Install PACKAGE to its own subdirectory under the configured target directory"""

    ctx.target = cfg["TARGETS"][kwargs["target"]]

    pip_run = CmdRunner(ctx, cfg["TARGETS"][kwargs["target"]], kwargs['password'])
    qip = Qip(ctx, pip_run)

    package = set_git_ssh(kwargs['package'])
    name, specs = qip.get_name_and_specs(package)

    version = '_'.join( (ver[0] + ver[1] for ver in specs) )
    has_dep_file = False
    # TODO: Remove depfile when out of alpha. It's not a reliable mechanism
    deps = {}
    if not kwargs['nodeps']:
        filename = kwargs['depfile']

        if os.path.isfile(filename):
            ctx.printer.status("Found a deps file for this package.")
            if click.confirm('Read deps from it?'):
                ctx.printer.status("Reading deps from file {}.".format(filename))
                deps = read_deps_from_file(name, specs, filename)
                has_dep_file = True
            else:
                ctx.printer.status("Fetching deps for {} and all its deps. "
                                   "This may take some time.".format(kwargs['package']))
                qip.fetch_dependencies(package, deps,)
        else:
            ctx.printer.status("Fetching deps for {} and all its deps. "
                               "This may take some time.".format(kwargs['package']))
            qip.fetch_dependencies(package, deps)

    deps[name] = specs

    ctx.printer.status("Dependencies resolved. Required packages:")
    ctx.printer.info("\t{}".format(', '.join(deps.keys())))
    if not ctx.yestoall and not click.confirm('Do you want to continue?'):
        sys.exit(0)
    if kwargs['depfile'] and not has_dep_file:
        write_deps_to_file(name, specs, deps, filename)

    for package, version in deps.iteritems():
        output, ret_code = qip.install_package(package, version, kwargs['download'])
        if ret_code == 0:
            ctx.printer.info(output.split('\n')[-2])



@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--target', '-t', prompt="Target to download for", default='centos72',
              type=click.Choice(cfg['TARGETS'].keys()))
@click.option('--password', prompt="Your password [leave blank if using ssh keys]",
              default="", hide_input=True)
def download(ctx, **kwargs):
    """Download PACKAGE to its own subdirectory under the configured target directory"""
    if (kwargs['package'].startswith("git@gitlab:") and
            not has_git_version(kwargs['package'])):
        ctx.printer.error("Please specify a version with `@` when installing from git")
        sys.exit(1)

    package_name = set_git_ssh(kwargs['package'])
    ctx.target = cfg["TARGETS"][kwargs["target"]]
    pip_run = CmdRunner(ctx, ctx.target, kwargs['password'])

    qip = Qip(ctx, pip_run)
    # Specs are already part of the package_name in this case
    qip.download_package(package_name, None)


def main(arguments=None):
    qipcmd()