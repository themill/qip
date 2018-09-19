# :coding: utf-8

import click
import _version as ver
import sys
import mlog
import os
import shutil

from qipcore import QipError, Qip, QipPackageInstalled


class QipContext(object):
    logger = None
    yestoall = {}


def set_git_ssh(package):
    """
    Replace the gitlab copied prefix with the one for pip
    """
    if package.startswith("git@gitlab:"):
        package = "git+ssh://" + package.replace(":", "/")
    return package


def configure_mlog(verbose):
    mlog.configure()
    logger = mlog.Logger(__name__ + ".main")
    mlog.root.handlers["stderr"].filterer.filterers[0].levels = mlog.levels

    # Ensure we are always at warning at least
    if verbose < 1:
        verbose = 1
    try:
        # Get the mlog verbosity from cli option, capped to max levels
        verbosity = mlog.levels[::-1][min(verbose, len(mlog.levels)-1)]
    except IndexError:
        verbosity = "warning"

    mlog.root.handlers["stderr"].filterer.filterers[0].min = verbosity
    return logger


@click.command()
@click.version_option(version=ver.__version__)
@click.option("-v", "--verbose", count=True)
@click.option("-y", is_flag=True, help="Yes to all prompts")
@click.argument("package")
@click.option("--nodeps", "-n", is_flag=True,
              help="Install the specified package without deps")
@click.option("--outdir", "-o", help="Directory to install package to",
              default="")
def install(**kwargs):
    """Install PACKAGE to its own subdirectory under the requested
    target directory
    """
    logger = configure_mlog(kwargs["verbose"])

    if kwargs["outdir"] == "":
        logger.error("Please specify an output directory.")
        sys.exit(1)

    qip = Qip(kwargs["outdir"], logger)

    package = set_git_ssh(kwargs["package"])
    try:
        name, specs = qip.get_name_and_specs(package)
    except QipError:
        logger.error("Please specify a version with `@` "
                     "when installing from git")
        sys.exit(1)

    deps = {}
    if not kwargs["nodeps"]:
        logger.info("Fetching deps for {} and all its deps. "
                    "This may take some time."
                    .format(kwargs["package"]), user=True)
        try:
            qip.fetch_dependencies(package, deps)
        except QipError as e:
            logger.error(e)
            sys.exit(1)

    deps[name] = specs

    if not os.path.exists(kwargs["outdir"]):
        try:
            os.makedirs(kwargs["outdir"])
        except os.error:
            logger.error("Unable to create target dir {}"
                         .format(kwargs["outdir"]))
            sys.exit(1)

    logger.info("Dependencies resolved. Required packages:", user=True)
    logger.info("\t{}".format(", ".join(deps.keys())), user=True)
    if not kwargs["y"] and not click.confirm("Do you want to continue?"):
        sys.exit(0)

    for package, specs in deps.iteritems():
        specs = ",".join((x[0]+x[1] for x in specs))
        logger.info("Installing {} : {}".format(package, specs),
                    user=True)
        try:
            output, ret_code = qip.install_package(package, specs,
                                                   kwargs["y"])

        except QipError as e:
            logger.error(e.message)
            sys.exit(1)

        except QipPackageInstalled as e:
            logger.warning(e.message)
            if click.confirm("Do you want to overwrite it?"):
                qip.rmtree(e.target_dir)
                output, ret_code = qip.install_package(package, specs,
                                                       True)
            else:
                logger.info("Skipping installation of {}."
                            .format(package), user=True)
                continue

        if ret_code == 0:
            logger.info(output.split("\n")[-2], user=True)


def main(arguments=None):
    install()
