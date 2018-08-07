# :coding: utf-8

from pkg_resources import Requirement as Req
import click
import os
import re
from cmdrunner import CmdRunner


class QipError(Exception):
    pass


def has_git_version(package):
    """ Regex to test if a gitlab URL has a version specified

    :param package: Gitlab url of the package
    :returns: True if tag/version present in URL. False otherwise
    """
    m = re.search(r'\.git@.+$', package)
    if m is None:
        return False
    return True


class Qip(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.runner = CmdRunner(ctx)

    def download_package(self, package, version):
        """
        Download *package* with *spec* from Pypi or gitlab. Returns
        *False* if unable to do so, and *True* if successful.

        :param package: Name of pacakge to download
        :param version: The version spec of the package
        :returns: True if download successful, False otherwise.
        """
        if version:
            spec = ','.join((ver[0] + ver[1] for ver in version))
        else:
            spec = ''

        cmd = (
            "pip download --no-deps --exists-action a --dest {0} --no-cache "
            "--find-links {0}".format(self.ctx.target["package_idx"])
            )

        cmd += " '{}{}'".format(package, spec)
        self.ctx.mlogger.info("Downloading {0}{1}".format(package, spec),
                              user=True)
        output, stderr, ret_code = self.runner.run_pip(cmd)

        output = output.split('\n')[1].strip()
        if output.startswith('File was already downloaded'):
            self.ctx.mlogger.info("{0}".format(output), user=True)
            self.ctx.mlogger.info("Package exists. Download skipped.",
                                  user=True)
            return True

        if ret_code != 0:
            self.ctx.mlogger.error("Unable to download requested package. "
                                   "Reason from pip below")
            self.ctx.mlogger.error(stderr)
            self.ctx.mlogger.error("If this is a package from Gitlab you "
                                   "should download it first.")
            return False

        self.ctx.mlogger.info("Package {0} {1} downloaded.".
                              format(package, spec), user=True)
        return True

    def get_name_and_specs(self, package):
        """ Get the specs of the package from provided name. If there
        are no specs as part of the package name it uses pip to
        get the latest version

        :parm package: The name of the package or Gitlab URL
        :returns: A tuple of the name and version specs for the package
        """
        if package.startswith("git+ssh://"):
            if not has_git_version(package):
                raise QipError()

            package_name = os.path.basename(package)
            name, specs = package_name.split('.git@')
            specs = [('==', specs)]
        else:
            pkg_req = Req.parse(package)
            name = pkg_req.unsafe_name
            specs = pkg_req.specs

            if not specs:
                # If the package has no version specified grab the latest one
                test_cmd = (
                    "pip install --ignore-installed --find-links"
                    " {0} '{1}=='".format(self.ctx.target["package_idx"], name)
                )
                output, stderr, ret_code = self.runner.run_pip(test_cmd)
                match = re.search(r"\(from versions: ((.*))\)", output)
                if match:
                    version = match.group(1).split(", ")[-1]
                    specs = [('==', version)]

        return name, specs

    def fetch_dependencies(self, package, deps_install):
        """
        Recursively fetch dependencies for *package*. Populates the
        *deps_install* dictionary passed to it with the package name
        and version specs [name: specs]. *deps_install* is a list that
        will be populated with the package details to install later.

        :param package: The package name for which to get dependecies
        :param deps_install: List of the dependencies to install later
        """
        self.ctx.mlogger.info("Resolving deps for {}".format(package),
                              user=True)
        cmd = (
            "pip download --exists-action w '{0}' "
            "-d /tmp --no-binary :all: --find-links {1} --no-cache"
            "| grep Collecting | cut -d' ' "
            "-f2 | grep -v '{0}'".
            format(package, self.ctx.target["package_idx"])
        )
        output, stderr, _ = self.runner.run_pip(cmd)
        deps = output.split()

        for dep in deps:
            pkg_req = Req.parse(dep)
            name = pkg_req.unsafe_name
            specs = pkg_req.specs
            if name in deps_install.keys():
                self.ctx.mlogger.info("\tSkipping {}. Already processed. ".
                                      format(name), user=True)
                continue
            deps_install[name] = specs
            self.fetch_dependencies(dep, deps_install)

    def install_package(self, package, version):
        """
        Install a *package* of *version*.

        :param package: Name of package to install
        :param version: the version spec for the package
        :returns: a tuple of the command output and return code
        """
        spec = ','.join((ver[0] + ver[1] for ver in version))
        self.ctx.mlogger.info("Installing {} : {}".format(package, spec),
                              user=True)
        temp_dir = None

        # Need this to catch hard exists and clean up temp dir
        try:
            temp_dir, exit_status = self.runner.mkdtemp("/tmp")
            if exit_status != 0:
                raise QipError("Unable to create temp directory")

            cmd = (
                "pip install --ignore-installed --no-deps --prefix {0}"
                " --no-index --no-cache-dir --find-links {1}"
                " '{2}{3}'".format(temp_dir, self.ctx.target['package_idx'],
                                   package, spec)
            )

            output, stderr, ret_code = self.runner.run_pip(cmd)

            lastline = output.split('\n')[-2].strip()
            m = re.search(r'(\S+-[\d\.]+)$', lastline)
            if m:
                if os.path.isdir(
                    "{0}/{1}".format(self.ctx.target['install_dir'],
                                     m.group(1))
                ):
                    self.ctx.mlogger.warning(
                        "Package {} already installed to index.".
                        format(m.group(1))
                    )
                    if (not self.ctx.yestoall and not
                       click.confirm("Overwrite it?")):
                        self.runner.rmtree(temp_dir)
                        return "", 1

                self.runner.install_and_sync(
                    temp_dir, "{0}/{1}".
                    format(self.ctx.target['install_dir'], m.group(1))
                )

            return output, ret_code
        finally:
            if temp_dir:
                self.runner.rmtree(temp_dir)

    def check_to_download(self, package, output):
        """
        Confirmation prompt if the requested *package* is not found. Parses
        *output* to see if package is missing. Returns *True* if user wishes
        to download the package, *False* otherwise
        """
        output = output.split('\n')[-2]
        if output.startswith("No matching distribution found for"):
            self.ctx.mlogger.info("{0} not found in package index.".
                                  format(package), user=True)
            self.ctx.mlogger.info("Downloading it....", user=True)
            return True
        return False
