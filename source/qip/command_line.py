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
from pkg_resources import Requirement as Req
from distutils.dir_util import copy_tree

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
def qipcmd(ctx):
    """Install or download Python packages to an isolated location."""
    mlog.configure()
    qctx = QipContext()
    qctx.logger = mlog.Logger(__name__ + ".main")
    ctx.obj = qctx


def set_git_ssh(package):
    if package.startswith("git@gitlab:"):
        package = 'git+ssh://' + package.replace(':', '/')
    return package


def has_git_version(package):
    m = re.search(r'\.git@.+$', package)
    if m is None:
        return False
    return True


def fetch_dependencies(ctx, package, deps_install):
    ctx.logger.info("Resolving deps for {}".format(package))
    cmd = ("pip download --exists-action w '{0}' "
           "-d /tmp --no-binary :all: --find-links {1} --no-cache"
           "| grep Collecting | cut -d' ' "
           "-f2 | grep -v '{0}'".format(package, cfg["PACKAGE_INDEX"]))
    output, _ = run_pip_command(cmd)
    deps = output[0].split()

    #ctx.logger.info("\tDeps resolved: {}".format(deps))

    for dep in deps:
        pkg_req = Req.parse(dep)
        name = pkg_req.unsafe_name
        specs = pkg_req.specs
        if name in deps_install.keys():
            ctx.logger.info("\tSkipping {}. Already processed. ".format(name))
            continue
        deps_install[name] = specs
        fetch_dependencies(ctx, dep, deps_install)


def is_installed(package, version):
    if os.path.exists("{1}/{0}".format(package, cfg["INSTALL_DIR"])):
        ctx.logger.info("{} already installed".format(package))
        return True
    else:
        return False


def run_pip_command(cmd):
    #print "RUNNING: ", cmd
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ps.communicate()
    return output, ps.returncode


def write_deps_to_file(name, specs, deps, filename):
    with open(filename, 'w') as fh:
        json.dump(deps, fh)


def read_deps_from_file(name, specs, filename):
    with open(filename, 'r') as fh:
        deps = json.load(fh)
    return deps


def check_to_download(ctx, package, spec, output):
    if output[1].split('\n')[-2].startswith("No matching distribution found for"):
        ctx.logger.warning("{0} not found in package index.".format(package))
        return click.confirm('Do you want to try and download it now?')
    return False


def download_package(ctx, package, spec):
    cmd = ("pip download --no-deps --exists-action w "
           "--dest {0} --no-cache --find-links {0}".format(cfg["PACKAGE_INDEX"])
          )

    if not spec:
        spec = ''
    cmd += " '{}{}'".format(package, spec)
    ctx.logger.info("Downloading {0} {1}".format(package, spec))
    output, ret_code = run_pip_command(cmd)

    if ret_code != 0:
        ctx.logger.error("Unable to download requested package. Reason from pip below")
        ctx.logger.error(output[1])
        ctx.logger.warning("If this is a package from Gitlab you should download it first.")
        return False

    return True


def install_package(ctx, package, version, download=False):
    spec = ','.join( (ver[0] + ver[1] for ver in version) )
    ctx.logger.info("Installing {} : {}".format(package, spec))

    try:
        temp_dir = tempfile.mkdtemp(dir=cfg["INSTALL_DIR"])
    except OSError:
        ctx.logger.error("Unable to create temp directory")
        sys.exit(1)

    cmd = ("pip install --ignore-installed --no-deps --prefix {0}"
           " --no-index --no-cache-dir --find-links {1}"
           " '{2}{3}'".format(temp_dir, cfg["PACKAGE_INDEX"], package, spec)
          )

    output, ret_code = run_pip_command(cmd)
    if ret_code == 1:
        if not download and not check_to_download(ctx, package, spec, output):
            ctx.logger.warning("Not downloading {}. Skipping installation.".format(package))
            shutil.rmtree(temp_dir)
        else:
            shutil.rmtree(temp_dir)
            if not download_package(ctx, package, spec):
                return
            install_package(ctx, package, version)
    else:
        lastline = output[0].split('\n')[-2].strip()
        m = re.search(r'(\S+-[\d\.]+)$', lastline)
        if m:
            try:
                os.rename(temp_dir, "{0}/{1}".format(cfg["INSTALL_DIR"], m.group(1)))
            except OSError:
                shutil.rmtree(temp_dir)


@qipcmd.command()
@click.pass_obj
@click.argument('package')
@click.option('--nodeps', is_flag=True, help='Just install the specified package without deps')
@click.option('--download', is_flag=True, help='Download packages without prompting')
def install(ctx, **kwargs):
    """Install PACKAGE to its own subdirectory under the configured target directory"""

    package = set_git_ssh(kwargs['package'])
    if package.startswith("git+ssh://"):
        if not has_git_version(package):
            ctx.logger.error("Please specify a version with `@` when installing from git")
            sys.exit(1)
        package_name = os.path.basename(package)
        name, specs = package_name.split('.git@')
        specs = [('==', specs)]
    else:
        pkg_req = Req.parse(package)
        name = pkg_req.unsafe_name
        specs = pkg_req.specs

    version = '_'.join( (ver[0] + ver[1] for ver in specs) )
    filename = os.path.join(cfg["DEP_STORE"], "{}-{}".format(name, version))
    has_dep_file = False

    if not kwargs['nodeps']:
        if os.path.isfile(filename):
            ctx.logger.info("Found a deps file for this package.")
            if click.confirm('Read deps from it?'):
                ctx.logger.info("Reading deps from file {}.".format(filename))
                deps = read_deps_from_file(name, specs, filename)
                has_dep_file = True
            else:
                deps = {}
                ctx.logger.info("Fetching deps for {} and all its deps. This may take some time.".format(kwargs['package']))
                fetch_dependencies(ctx, package, deps)
        else:
            deps = {}
            ctx.logger.info("Fetching deps for {} and all its deps. This may take some time.".format(kwargs['package']))
            fetch_dependencies(ctx, package, deps)

    deps[name] = specs

    ctx.logger.info("Dependencies resolved. Required packages:")
    ctx.logger.info("\t{}".format(', '.join(deps.keys())))
    if not click.confirm('Do you want to continue?'):
        sys.exit(0)
    if not has_dep_file:
        write_deps_to_file(name, specs, deps, filename)

    for package, version in deps.iteritems():
        #ctx.logger.info("Installing {} : {}".format(package, version))
        install_package(ctx, package, version, kwargs['download'])
    # if deps:
    #     ctx.logger.info("Installing deps as needed.")
    #     for dep in deps:
    #         install_package(ctx, dep)
    # else:
    #     ctx.logger.info("No deps required.")

    # # Install the actual package now
    # install_package(ctx, kwargs['package'])


@qipcmd.command()
@click.pass_obj
@click.argument('package')
def download(ctx, **kwargs):
    """Download PACKAGE to its own subdirectory under the configured target directory"""
    if not has_git_version(kwargs['package']):
        ctx.logger.error("Please specify a version with `@` when installing from git")
        sys.exit(1)

    package_name = set_git_ssh(kwargs['package'])
    # Specs are already part of the package_name
    download_package(ctx, package_name, None)


def main(arguments=None):
    qipcmd()