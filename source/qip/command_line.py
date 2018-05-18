# :coding: utf-8
import click
import subprocess
import _version as ver
import mlog
import re
import os

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
    #qctx.target_conf_dict = initialise_target_configurations()
    #qctx.config = config_reader.read_config()
    ctx.obj = qctx


def fetch_dependencies(package):
    cmd = "pip download {0} -d /tmp --no-binary :all: | grep Collecting | cut -d' ' -f2 | grep -v {0}".format(package)
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    return output.split()


def is_package_installed(package):
    if os.path.exists("/tmp/qip-test/{}".format(package)):
        print "{} already installed".format(package)
        return True
    else:
        return False

def install_package(package):
    m = re.match(r"(\w*)[><=]+([\d\.]+)", package)
    print "Install: ", package
    # if package does not end with number, get version
    if m is None:
        cmd = "pip install {}==".format(package)
        pip_cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = pip_cmd.communicate()[0]
        match = re.search(r"\(from versions: ((.*))\)", output)
        if match:
            latest_version = match.group(1).split(", ")[-1]

        if is_package_installed('{0}-{1}'.format(package, latest_version)):
            return

        cmd = "pip install --install-option='--prefix=/tmp/qip-test/{0}-{1}' {0}=={1}".format(package, latest_version)
    else:
        if is_package_installed('{0}-{1}'.format(m.group(1), m.group(2))):
            return
        cmd = "pip install --install-option='--prefix=/tmp/qip-test/{0}-{1}' {0}".format(m.group(1), m.group(2))
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print output


@qipcmd.command()
@click.pass_obj
@click.argument('package')
def install(ctx, **kwargs):
    deps = fetch_dependencies(kwargs['package'])
    print deps

    for dep in deps:
        install_package(dep)

    install_package(kwargs['package'])

    #ctx.logger.error(
    #    "Failed to install {!r}"
    #    .format(kwargs['package']),
    #    traceback=True
    #)


def main(arguments=None):
    qipcmd()