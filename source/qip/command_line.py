# :coding: utf-8

import click
import _version as ver
import sys
import mlog
import platform
import os

import config
from qipcore import QipError, Qip, QipPackageInstalled


cfg = config.Config()
cfg.from_pyfile("configs/base.py")
cfg.from_envvar("QIP_CONFIG", silent=True)


class QipContext(object):
    logger = None
    target_conf_dict = {}
    cfg = None
    target = None
    password = ""


def get_target(ctx, param, value):
    """ Prompt the user to select a target from the known
    targets. If one is specified in the commandline, this
    simply returns the target dictionary.

    :returns: dictionary containing target config
    """
    targets = sorted(cfg['TARGETS'].keys())
    if value in targets:
        return cfg['TARGETS'][value]

    print("Targets:")
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
    """ Prompt user for password if remote is not localhost

    :returns: string containing password
    """
    password = ""
    if ctx.params["target"]["server"] != "localhost":
        password = click.prompt(
            "User password (blank for keys)",
            hide_input=True, default="", show_default=False
        )
    return password


@click.group()
@click.pass_context
@click.version_option(version=ver.__version__)
@click.option("-v", '--verbose', count=True)
@click.option("-y", is_flag=True, help="Yes to all prompts")
@click.option('--target', '-t', callback=get_target)
@click.option('--password', callback=get_password, hide_input=True)
def qipcmd(ctx, verbose, y, target, password):
    """Install Python packages to an isolated location."""
    qctx = QipContext()

    global cfg
    cfg.from_envvar("QIP_CONFIG", silent=True)

    qctx.cfg = cfg

    qctx.yestoall = y
    qctx.target = target
    qctx.password = password

    mlog.configure()
    qctx.mlogger = mlog.Logger(__name__ + ".main")

    mlog.root.handlers["stderr"].filterer.filterers[0].levels = mlog.levels
    try:
        # Get the mlog verbosity from cli option, capped to max levels
        verbosity = mlog.levels[::-1][min(verbose, len(mlog.levels)-1)]
    except IndexError:
        verbosity = 'warning'

    mlog.root.handlers["stderr"].filterer.filterers[0].min = verbosity

    ctx.obj = qctx


def set_git_ssh(package):
    """
    Replace the gitlab copied prefix with the one for pip
    """
    if package.startswith("git@gitlab:"):
        package = 'git+ssh://' + package.replace(':', '/')
    return package


def set_target_platform(target):
    distro = platform.release()
    distro = "-".join(distro.split('.')[-2:]).replace('_', '-')
    for k, v in target.iteritems():
        target[k] = v.replace('{{platform}}', distro)

    return target


def check_paths_exist(target):
    if not os.path.exists(target['install_dir']):
        raise QipError("Install directory ({}) does not exist."
                       .format(target['install_dir']))


@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--nodeps', '-n', is_flag=True,
              help='Install the specified package without deps')
def install(ctx, **kwargs):
    """Install PACKAGE to its own subdirectory under the configured
    target directory
    """
    set_target_platform(ctx.target)
    try:
        check_paths_exist(ctx.target)
    except QipError as e:
        ctx.mlogger.error(e.message)
        sys.exit(1)

    qip = Qip(ctx.target, ctx.password, ctx.mlogger)

    package = set_git_ssh(kwargs['package'])
    try:
        name, specs = qip.get_name_and_specs(package)
    except QipError as e:
        ctx.mlogger.error(e)
        sys.exit(1)

    deps = {}
    if not kwargs['nodeps']:
        ctx.mlogger.info("Fetching deps for {} and all its deps. "
                         "This may take some time."
                         .format(kwargs['package']), user=True)
        qip.fetch_dependencies(package, deps)

    deps[name] = specs

    ctx.mlogger.info("Dependencies resolved. Required packages:", user=True)
    ctx.mlogger.info("\t{}".format(', '.join(deps.keys())), user=True)
    if not ctx.yestoall and not click.confirm('Do you want to continue?'):
        sys.exit(0)

    for package, specs in deps.iteritems():
        spec_str = ','.join(["{}{}".format(s[0], s[1]) for s in specs])

        ctx.mlogger.info("Installing {} : {}".format(package, spec_str),
                         user=True)
        try:
            spec = ','.join((s[0] + s[1] for s in specs))
            overwrite = ctx.yestoall
            try:
                output, ret_code = qip.install_package(package, spec,
                                                       overwrite)
            except QipPackageInstalled as e:
                ctx.mlogger.warning(e, user=True)
                if (not ctx.yestoall and click.confirm("Overwrite it?")):
                    output, ret_code = qip.install_package(package, spec,
                                                           True)
                else:
                    continue

        except QipError as e:
            print(e.message)
            sys.exit(1)

        if ret_code == 0:
            ctx.mlogger.info(output.split('\n')[-2])


def main(arguments=None):
    qipcmd()
