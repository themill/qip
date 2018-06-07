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
    m = re.search(r'@.+$', package)
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

    ctx.logger.info("\tDeps resolved: {}".format(deps))

    for dep in deps:
        pkg_req = Req.parse(dep)
        name = pkg_req.unsafe_name
        specs = pkg_req.specs
        if name in deps_install.keys():
            ctx.logger.info("\t{} already processed. Skipping.".format(name))
            continue
        deps_install[name] = specs
        fetch_dependencies(ctx, dep, deps_install)


def is_package_installed(ctx, package):
    if os.path.exists("{1}/{0}".format(package, cfg["INSTALL_DIR"])):
        ctx.logger.info("{} already installed".format(package))
        return True
    else:
        return False


def run_pip_command(cmd):
    print "RUNNING: ", cmd
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ps.communicate()
    return output, ps.returncode


def check_to_download(ctx, package, output):
    if output[1].split('\n')[-2].startswith("No matching distribution found for"):
        ctx.logger.warning("{0} not found in package index.".format(package))
        if click.confirm('Do you want to try and download it now?'):
            if not download_package(ctx, package):
                return False
            install_package(ctx, package)
            return True

    return False


def download_package(ctx, package):
    cmd = "pip download --no-deps --exists-action w --dest {0} --find-links {0}".format(cfg["PACKAGE_INDEX"])
    to_download = set_git_ssh(package)

    cmd += " '{}'".format(to_download)
    ctx.logger.info("Downloading {0}".format(to_download))
    output, ret_code = run_pip_command(cmd)

    if ret_code != 0:
        ctx.logger.error("Unable to download requested package. Reason from pip below")
        ctx.logger.error(output[1])
        return False

    return True


def install_cmd_gitlab(ctx, package, target_dir):
    package = set_git_ssh(package)
    if not has_git_version(package):
        ctx.logger.error("Please specify a version with `@` when installing from git")
        sys.exit(1)

    package_name = os.path.basename(package)
    package_name, version = package_name.split('.git@')
    cmd = " '{1}' '{0}'".format(package, target_dir)
    return cmd


def install_cmd_pypi(ctx, package, target_dir):
    m = re.search(r"(.*)[><=]+([\d\.]+)", package)

    pkg_req = Req.parse(package)
    name = pkg_req.unsafe_name
    specs = pkg_req.specs

    cmd = ""
    # if package does not end with number, get version
    if not specs:
        test_cmd = "pip install --ignore-installed '{}=='".format(package)
        output, ret_code = run_pip_command(test_cmd)

        # This is expected to fail to give us a list of available versions
        match = re.search(r"\(from versions: ((.*))\)", output[1])
        if match:
            latest_version = match.group(1).split(", ")[-1]
        else:
            if not check_to_download(ctx, package, output):
                return

        if is_package_installed(ctx, '{0}-{1}'.format(package, latest_version)):
            return


        cmd = " '{2}' '{0}=={1}'".format(package, latest_version, target_dir)

    else:
        if is_package_installed(ctx, '{0}-{1}'.format(m.group(1), m.group(2))):
            return
        #Installing html2text<2016.5,>=2016.4.2
        cmd = " '{1}' '{0}'".format(name, target_dir)

    return cmd


def install_package(ctx, package):
    ctx.logger.info("Installing {} ".format(package))

    cmd = "pip install --ignore-installed --no-deps --prefix"
    temp_dir = tempfile.mkdtemp(dir=cfg["INSTALL_DIR"])
    if package.startswith("git@gitlab"):
        tmp_cmd = install_cmd_gitlab(ctx, package, temp_dir)
        if tmp_cmd is None:
            return
        cmd += tmp_cmd
    else:
        tmp_cmd = install_cmd_pypi(ctx, package, temp_dir)
        if tmp_cmd is None:
            return
        cmd += tmp_cmd

    cmd += " --no-index --no-cache-dir --find-links {0}".format(cfg["PACKAGE_INDEX"])
    output, ret_code = run_pip_command(cmd)
    if ret_code != 0:
        if not check_to_download(ctx, package, output):
            match = re.search(r"\(from versions: ((.*))\)", output[1])
            if not match:
                ctx.logger.error(output[1])
    else:
        lastline = output[0].split('\n')[-2].strip()
        m = re.search(r'(\S+-[\d\.]+)$', lastline)
        if m:
            # move directory
            os.rename(temp_dir, "{0}/{1}".format(cfg["INSTALL_DIR"], m.group(1)))
            #shutil.rmtree(temp_dir)


@qipcmd.command()
@click.pass_obj
@click.argument('package')
def install(ctx, **kwargs):
    """Install PACKAGE to its own subdirectory under the configured target directory"""

    ctx.logger.info("Fetching deps for {} and all its deps. This may take some time.".format(kwargs['package']))

    deps = {}

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

    deps[name] = specs

    fetch_dependencies(ctx, package, deps)
    print deps
    for package, version in deps.iteritems():
        ctx.logger.info("Installing {} : {}".format(package, version))
        #install_package(package, version)
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
    download_package(ctx, kwargs['package'])


def main(arguments=None):
    qipcmd()