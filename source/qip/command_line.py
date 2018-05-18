# :coding: utf-8
import click
import _version as ver
import mlog

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
    cmd = "pip download {0} -d /tmp --no-binary :all:".format(package)
    pip_down = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

    cmd = """pip download {0} -d /tmp --no-binary :all:
            | grep Collecting
            | cut -d' ' -f2
            | grep -v {0}""".format(package)
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print output


@qipcmd.command()
@click.pass_obj
@click.argument('package')
def install(ctx, **kwargs):

    ctx.logger.error(
        "Failed to install {!r}"
        .format(kwargs['package']),
        traceback=True
    )


def main(arguments=None):
    qipcmd()