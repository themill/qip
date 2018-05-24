# :coding: utf-8
import click
import subprocess
import _version as ver
import mlog
import re
import os

import config

cfg = config.Config()
cfg.from_envvar("CONFIG")
class QipContext(object):
    logger = None
    target_conf_dict = {}
    qip_config = {}


@click.group()
@click.pass_context
@click.version_option(version=ver.__version__)
def qipcmd(ctx):
    mlog.configure()
    qctx = QipContext()
    qctx.logger = mlog.Logger(__name__ + ".main")
    ctx.obj = qctx


def fetch_dependencies(package):
    cmd = "pip download {0} -d /tmp --no-binary :all: | grep Collecting | cut -d' ' -f2 | grep -v {0}".format(package)
    output, _ = run_pip_command(cmd)
    return output[0].split()


def is_package_installed(ctx, package):
    if os.path.exists("{1}/{0}".format(package, cfg["INSTALL_DIR"])):
        ctx.logger.info("{} already installed".format(package))
        return True
    else:
        return False


def run_pip_command(cmd):
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
    cmd = "pip download --exists-action a --dest {0} --find-links {0}".format(cfg["PACKAGE_INDEX"])
    to_download = package
    if to_download.startswith("git@gitlab:"):
        to_download = 'git+ssh://' + to_download.replace(':', '/')
    cmd += " {}".format(to_download)
    ctx.logger.info("Downloading {0}".format(to_download))
    output, ret_code = run_pip_command(cmd)

    if ret_code != 0:
        ctx.logger.error("Unable to download requested package. Reason from pip below")
        ctx.logger.error(output[1])
        return False

    return True


def install_package(ctx, package):
    m = re.match(r"(\w*)[><=]+([\d\.]+)", package)
    ctx.logger.info("Installing {} ".format(package))

    cmd = "pip install --no-deps --prefix"
    # if package does not end with number, get version
    if m is None:
        test_cmd = "pip install {}==".format(package)
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

        cmd += " {2}/{0}-{1} '{0}=={1}'".format(package, latest_version, cfg["INSTALL_DIR"])

    else:
        if is_package_installed(ctx, '{0}-{1}'.format(m.group(1), m.group(2))):
            return
        cmd += " {2}/{0}-{1} '{0}'".format(m.group(1), m.group(2), cfg["INSTALL_DIR"])

    cmd += " --no-index --no-cache-dir --find-links {0}".format(cfg["PACKAGE_INDEX"])
    output, ret_code = run_pip_command(cmd)
    if ret_code != 0:
        if not check_to_download(ctx, package, output):
            match = re.search(r"\(from versions: ((.*))\)", output[1])
            if not match:
                ctx.logger.error(output[1])


@qipcmd.command()
@click.pass_obj
@click.argument('package')
def install(ctx, **kwargs):
    ctx.logger.info("Fetching deps for {}".format(kwargs['package']))
    deps = fetch_dependencies(kwargs['package'])

    if deps:
        ctx.logger.info("Installing deps as needed.")
        for dep in deps:
            install_package(ctx, dep)
    else:
        ctx.logger.info("No deps required.")

    # Install the actual package now
    install_package(ctx, kwargs['package'])


@qipcmd.command()
@click.pass_obj
@click.argument('package')
def download(ctx, **kwargs):
    download_package(ctx, kwargs['package'])


def main(arguments=None):
    qipcmd()