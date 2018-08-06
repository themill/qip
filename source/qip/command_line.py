# :coding: utf-8

import click
import _version as ver
import os
import sys
import json
import mlog

import config
from qipcore import Qip, has_git_version


cfg = config.Config()
cfg.from_pyfile("configs/base.py")


class QipContext(object):
    logger = None
    target_conf_dict = {}
    qip_config = {}
    target = None
    password = ""


@click.group()
@click.pass_context
@click.version_option(version=ver.__version__)
@click.option("-v", '--verbose', count=True)
@click.option("-y", is_flag=True, help="Yes to all prompts")
@click.option('--target', '-t', default=None)
def qipcmd(ctx, verbose, y, target):
    """Install or download Python packages to an isolated location."""
    cfg.from_envvar("QIP_CONFIG", silent=True)

    qctx = QipContext()
    qctx.yestoall = y
    qctx.target = target

    mlog.configure()
    qctx.mlogger = mlog.Logger(__name__ + ".main")

    mlog.root.handlers["stderr"].filterer.filterers[0].levels = mlog.levels

    try:
        verbosity = mlog.levels[::-1][verbose]
    except IndexError:
        verbosity = 'warning'
    mlog.root.handlers["stderr"].filterer.filterers[0].min = verbosity

    ctx.obj = qctx


def get_target(ctx, param, value):
    targets = sorted(cfg['TARGETS'].keys())
    if value in targets:
        return cfg['TARGETS'][value]

    print "Targets:"
    for i, t in enumerate(targets):
        print("[{}]  {}".format(i, t))
    print
    target = click.prompt(
        "Select a target",
        default=0,
        type=click.IntRange(0, len(targets) - 1, clamp=True),
        show_default=True
    )
    target = cfg['TARGETS'][targets[target]]

    return target


def get_password(ctx, param, value):
    password = ""
    if ctx.params["target"]["server"] != "localhost":
        password = click.prompt(
            "User password (blank for keys)",
            hide_input=True, default="", show_default=False
        )
    return password


def set_git_ssh(package):
    """
    Replace the gitlab copied prefix with the one for pip
    """
    if package.startswith("git@gitlab:"):
        package = 'git+ssh://' + package.replace(':', '/')
    return package


@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--target', callback=get_target)
@click.option('--password', callback=get_password, hide_input=True)
@click.option('--nodeps', '-n', is_flag=True, help='Install the specified package without deps')
def install(ctx, **kwargs):
    """Install PACKAGE to its own subdirectory under the configured
    target directory"""

    ctx.target = kwargs["target"]
    ctx.password = kwargs["password"]

    qip = Qip(ctx)

    package = set_git_ssh(kwargs['package'])
    name, specs = qip.get_name_and_specs(package)

    version = '_'.join((ver[0] + ver[1] for ver in specs))
    deps = {}
    if not kwargs['nodeps']:
        ctx.printer.status("Fetching deps for {} and all its deps. "
                           "This may take some time.".format(kwargs['package']))
        qip.fetch_dependencies(package, deps)

    deps[name] = specs

    ctx.mlogger.info("Dependencies resolved. Required packages:")
    ctx.mlogger.info("\t{}".format(', '.join(deps.keys())))
    if not ctx.yestoall and not click.confirm('Do you want to continue?'):
        sys.exit(0)

    for package, version in deps.iteritems():
        qip.download_package(package, version)

    for package, version in deps.iteritems():
        output, ret_code = qip.install_package(package, version)
        if ret_code == 0:
            ctx.mlogger.info(output.split('\n')[-2])


@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--target', callback=get_target)
@click.option('--password', callback=get_password, hide_input=True)
def download(ctx, **kwargs):
    """Download PACKAGE to its own subdirectory under the configured
    target directory"""
    if (kwargs['package'].startswith("git@gitlab:") and
            not has_git_version(kwargs['package'])):
        ctx.mlogger.error("Please specify a version with `@` "
                          "when installing from git")
        sys.exit(1)

    package_name = set_git_ssh(kwargs['package'])
    ctx.target = kwargs["target"]
    ctx.password = kwargs["password"]

    qip = Qip(ctx)
    # Specs are already part of the package_name in this case
    qip.download_package(package_name, None)


def main(arguments=None):
    qipcmd()
