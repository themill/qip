# :coding: utf-8
import click
import subprocess
import _version as ver
import mlog
import re
import os
import sys
import tempfile
import shutil
import json

import config
from printer import Printer
from pkg_resources import Requirement as Req
from distutils.dir_util import copy_tree
from remotecmd import RemoteCmd

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
@click.option('-v', '--verbose', count=True)
def qipcmd(ctx, verbose):
    """Install or download Python packages to an isolated location."""
    mlog.configure()
    qctx = QipContext()
    qctx.printer = Printer(verbose)
    qctx.logger = mlog.Logger(__name__ + ".main")
    mlog.root.handlers["stderr"].filterer.filterers[0].levels = mlog.levels
    verbose += 2
    try:
        verbosity = mlog.levels[::-1][verbose]
    except IndexError:
        verbosity = 'debug'

    mlog.root.handlers["stderr"].filterer.filterers[0].min = verbosity

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


def fetch_dependencies(ctx, package, deps_install):
    """
    Recursively fetch dependencies for *package*. Populates the
    *deps_install* dictionary passed to it with the package name
    and version specs [name: specs]
    """
    ctx.printer.status("Resolving deps for {}".format(package))
    cmd = ("pip download --exists-action w '{0}' "
           "-d /tmp --no-binary :all: --find-links {1} --no-cache"
           "| grep Collecting | cut -d' ' "
           "-f2 | grep -v '{0}'".format(package, cfg["PACKAGE_INDEX"]))
    output, _ = run_pip_command(cmd, ctx)
    deps = output[0].split()

    for dep in deps:
        pkg_req = Req.parse(dep)
        name = pkg_req.unsafe_name
        specs = pkg_req.specs
        if name in deps_install.keys():
            ctx.printer.info("\tSkipping {}. Already processed. ".format(name))
            continue
        deps_install[name] = specs
        fetch_dependencies(ctx, dep, deps_install)


def run_pip_command(cmd, ctx):
    """
    Execute the *cmd* using Popen and return (output, returncode) tuple
    """
    ctx.printer.debug("RUNNING: {}".format(cmd))
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ps.communicate()
    ctx.printer.debug("\t\tOUTPUT: {}".format(output))
    return output, ps.returncode


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


def check_to_download(ctx, package, spec, output):
    """
    Confirmation prompt if the requested *package* is not found. Parses
    *output* to see if packge is missing. Returns *True* if user wishes
    to download the package, *False* otherwise
    """
    print output.split('\n')
    if output.split('\n')[-2].startswith("No matching distribution found for"):
        ctx.printer.warning("{0} not found in package index.".format(package))
        return click.confirm('Do you want to try and download it now?')
    return False


def download_package(ctx, pip_run, package, spec):
    """
    Download *package* with *spec* from Pypi or gitlab. Returns
    *False* if unable to do so, and *True* if successful.
    """
    cmd = ("pip download --no-deps --exists-action w "
           "--dest {0} --no-cache --find-links {0}".format(cfg["PACKAGE_INDEX"])
          )

    if not spec:
        spec = ''
    cmd += " '{}{}'".format(package, spec)
    ctx.printer.status("Downloading {0} {1}".format(package, spec))
    output, stderr, ret_code = pip_run.run_remote_pip(cmd)

    if ret_code != 0:
        ctx.printer.error("Unable to download requested package. Reason from pip below")
        ctx.printer.error(stderr)
        ctx.printer.warning("If this is a package from Gitlab you should download it first.")
        return False
    ctx.printer.status("Package {0} {1} downloaded.".format(package, spec))
    return True


def install_package(ctx, pip_run, package, version, download=False):
    """
    Install a *package* of *version*. If download is *True* will
    automatically download the package first, otherwise will prompt
    to download
    """
    spec = ','.join( (ver[0] + ver[1] for ver in version) )
    ctx.printer.status("Installing {} : {}".format(package, spec))

    try:
        temp_dir = pip_run.mkdtemp(dir=cfg["INSTALL_DIR"])
    except OSError:
        ctx.printer.error("Unable to create temp directory")
        sys.exit(1)

    cmd = ("pip install --ignore-installed --no-deps --prefix {0}"
           " --no-index --no-cache-dir --find-links {1}"
           " '{2}{3}'".format(temp_dir, cfg["PACKAGE_INDEX"], package, spec)
          )

    output, stderr, ret_code = pip_run.run_remote_pip(cmd)
    if ret_code == 1:
        if not download and not check_to_download(ctx, package, spec, output):
            ctx.printer.warning("Not downloading {}. Skipping installation.".format(package))
            pip_run.rmtree(temp_dir)
        else:
            pip_run.rmtree(temp_dir)
            if not download_package(ctx, pip_run, package, spec):
                return
            install_package(ctx, pip_run, package, version)
    else:
        print "==================== ", output
        lastline = output.split('\r')[-2].strip()
        m = re.search(r'(\S+-[\d\.]+)$', lastline)
        if m:
            try:
                pip_run.rename_dir(temp_dir,
                                   "{0}/{1}".format(cfg["INSTALL_DIR"], m.group(1)))
            except OSError:
                pip_run.rmtree(temp_dir)
    return output, ret_code


@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--nodeps', '-n', is_flag=True, help='Install the specified package without deps')
@click.option('--download', '-d', is_flag=True, help='Download packages without prompting')
@click.option('--depfile', default=None, help='Use json file to get deps')
@click.option('--target', '-t', prompt="Target to install to", default='centos65',
              type=click.Choice(cfg['TARGETS'].keys()))
@click.option('--password', prompt="Your password", hide_input=True)
def install(ctx, **kwargs):
    """Install PACKAGE to its own subdirectory under the configured target directory"""

    package = set_git_ssh(kwargs['package'])
    if package.startswith("git+ssh://"):
        if not has_git_version(package):
            ctx.printer.error("Please specify a version with `@` when installing from git")
            sys.exit(1)
        package_name = os.path.basename(package)
        name, specs = package_name.split('.git@')
        specs = [('==', specs)]
    else:
        pkg_req = Req.parse(package)
        name = pkg_req.unsafe_name
        specs = pkg_req.specs

        if not specs:
            # If the package has no version specified grab the latest one
            test_cmd = ("pip install --ignore-installed --find-links"
                        " {0} '{1}=='".format(cfg["PACKAGE_INDEX"], name))
            output, ret_code = run_pip_command(test_cmd, ctx)
            match = re.search(r"\(from versions: ((.*))\)", output[1])
            if match:
                version = match.group(1).split(", ")[-1]
                specs = [('==', version)]

    version = '_'.join( (ver[0] + ver[1] for ver in specs) )
    filename = os.path.join(cfg["DEP_STORE"], "{}-{}".format(name, version))
    has_dep_file = False

    if not kwargs['nodeps']:
        if kwargs['depfile']:
            filename = kwargs['depfile']

        if os.path.isfile(filename):
            ctx.printer.status("Found a deps file for this package.")
            if click.confirm('Read deps from it?'):
                ctx.printer.status("Reading deps from file {}.".format(filename))
                deps = read_deps_from_file(name, specs, filename)
                has_dep_file = True
            else:
                deps = {}
                ctx.printer.status("Fetching deps for {} and all its deps. This may take some time.".format(kwargs['package']))
                fetch_dependencies(ctx, package, deps)
        else:
            deps = {}
            ctx.printer.status("Fetching deps for {} and all its deps. This may take some time.".format(kwargs['package']))
            fetch_dependencies(ctx, package, deps)

    deps[name] = specs

    ctx.printer.status("Dependencies resolved. Required packages:")
    ctx.printer.info("\t{}".format(', '.join(deps.keys())))
    if not click.confirm('Do you want to continue?'):
        sys.exit(0)
    if not has_dep_file:
        write_deps_to_file(name, specs, deps, filename)

    pip_run = RemoteCmd(ctx, cfg, kwargs['target'], kwargs['password'])
    for package, version in deps.iteritems():
        output, ret_code = install_package(ctx, pip_run, package, version, kwargs['download'])
        if ret_code == 0:
            ctx.printer.info(output[0].split('\n')[-2])


@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--password', prompt="Your password", hide_input=True)
def download(ctx, **kwargs):
    """Download PACKAGE to its own subdirectory under the configured target directory"""
    if kwargs['package'].startswith("git@gitlab:") and not has_git_version(kwargs['package']):
        ctx.printer.error("Please specify a version with `@` when installing from git")
        sys.exit(1)

    package_name = set_git_ssh(kwargs['package'])
    pip_run = RemoteCmd(ctx, cfg, "centos65", kwargs['password'])

    # Specs are already part of the package_name in this case
    download_package(ctx, pip_run, package_name, None)


def main(arguments=None):
    qipcmd()