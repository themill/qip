# :coding: utf-8

import os
import re
import wiz
import uuid
import subprocess
from pkg_resources import Requirement as Req


class QipError(Exception):
    pass


class QipPackageInstalled(Exception):
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
    def __init__(self, outdir, logger):
        self.outdir = outdir
        self.logger = logger

    def get_name_and_specs(self, package):
        """ Get the specs of the package from provided name. If there
        are no specs as part of the package name it uses pip to
        get the latest version

        :parm package: The name of the package or Gitlab URL
        :returns: A tuple of the name and version specs for the package
        """
        if package.startswith("git+ssh://"):
            if not has_git_version(package):
                raise QipError("Please specify a version with `@` "
                               "when installing from git")

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
                    "pip install --ignore-installed {!r}==".format(name)
                )
                try:
                    output, stderr, ret_code = self.run_pip(test_cmd)
                except QipError as e:
                    raise e

                match = re.search(r"\(from versions: ((.*))\)", stderr)
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
        cmd = (
            "download --exists-action w '{0}' "
            "-d /tmp --no-binary :all: --no-cache"
            "| grep Collecting | cut -d' ' "
            "-f2 | grep -v '{0}'".
            format(package)
        )
        output, stderr, _ = self.run_pip(cmd)
        deps = output.split()

        for dep in deps:
            pkg_req = Req.parse(dep)
            name = pkg_req.unsafe_name
            specs = pkg_req.specs
            if name in deps_install.keys():
                self.logger.info("\tSkipping {}. Already satisfied. "
                                 .format(name), user=True)
                continue
            deps_install[name] = specs
            self.fetch_dependencies(dep, deps_install)

    def install_package(self, package, spec, overwrite=False):
        """
        Install a *package* of *version*.

        :param package: Name of package to install
        :returns: a tuple of the command output and return code
        """
        temp_dir = None

        # Need this to catch hard exists and clean up temp dir
        try:
            temp_dir, exit_status = self.mkdtemp("/tmp")
            if exit_status != 0:
                raise QipError("Unable to create temp directory")

            cmd = (
                "install --ignore-installed --no-deps --prefix {0}"
                " --no-cache-dir "
                " '{1}{2}'".format(temp_dir, package, spec)
            )
            try:
                output, stderr, ret_code = self.run_pip(cmd)
            except Exception:
                raise QipError()

            lastline = output.split('\n')[-2].strip()

            m = re.search(r'((\S+)-[\d\.]+)$', lastline)
            if m:
                outdir = os.path.join(self.outdir, m.group(2))
                _, _, exit_status = self.run_cmd("mkdir -p -m 755 {}".format(outdir))
                if exit_status != 0:
                    raise QipError("Unable to create install "
                                   "directory: {}", outdir)

                if os.path.isdir(
                    "{0}/{1}".format(outdir,
                                     m.group(1))

                ) and not overwrite:
                    raise QipPackageInstalled("Package {} already "
                                              "installed to index."
                                              .format(m.group(1)))

                self.install(
                    temp_dir, "{0}/{1}".
                    format(outdir, m.group(1))
                )

            return output, ret_code
        finally:
            if temp_dir:
                self.rmtree(temp_dir)

    def strip_output(self, stdout, stderr):
        # Strip shell colour code characters
        ansi_escape = re.compile(
            r'\x1B\[[0-?]*[ -/]*[@-~]', re.IGNORECASE | re.MULTILINE
        )

        stdout = u''.join(stdout)
        stdout = ansi_escape.sub('', stdout)

        stderr = u''.join(stderr)
        stderr = ansi_escape.sub('', stderr)

        return stdout, stderr

    def run_pip(self, cmd):
        cmd = "pip {}".format(cmd)
        context = wiz.resolve_context(["python==2.7.*"])
        stdout, stderr, exit_status = self.run_cmd(cmd, context["environ"])
        return stdout, stderr, exit_status

    def install(self, from_dir, to_dir):
        cmd = "rsync -azvl {0}/ {1}".format(from_dir, to_dir)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def mkdtemp(self, path):
        _file = os.path.join(path, "tmp" + uuid.uuid4().hex)
        _, _, exit_status = self.run_cmd("mkdir -m 755 {}".format(_file))
        return _file, exit_status

    def rmtree(self, path):
        cmd = "rm -rf {}".format(path)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def run_cmd(self, cmd, env=None):
        self.logger.debug("Running {0} ".
                          format(cmd,))

        ps = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        stdout, stderr = ps.communicate()

        stdout, stderr = self.strip_output(
            stdout.decode('utf-8'), stderr.decode('utf-8')
        )

        self.logger.debug(u"Command returned: \n"
                          "STDOUT: {0}\n"
                          "STDERR: {1}\n"
                          "Exit Code: {2}"
                          .format(stdout, stderr, ps.returncode))

        return stdout, stderr, ps.returncode
