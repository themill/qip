# :coding: utf-8

import os
import re
import wiz
import uuid
import subprocess
from pkg_resources import Requirement as Req
from exception import QipError, QipPackageInstalled


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
    """
    Core class for qip used to query dependencies, install packages,
    and execute pip commands in a wiz context.

    :ivar outdir: The directory into which packages will be installed
    :ivar logger: generally an instance of mlog used to print outputs
    :ivar dependency_tracker: a dictionary tracking dependencies that are
                              installed with a package. See the
                              `set_dependencies function
                              <apigit+ssh://git@gitlab/rnd/mlog.git@0.2.1_reference/core.html#qip.core.Qip.set_dependecies>`__
                              for more info on its layout
    """
    def __init__(self, outdir, logger):
        self.outdir = outdir  #: outdir initial value: ``outdir``
        self.logger = logger  #: initial value: ``logger``
        self.dependency_tracker = dict()  #: initial value: ``dict()``

    def get_name_and_specs(self, package):
        """ Get the specs of the package from provided name. If there
        are no specs as part of the package name it uses pip to
        get the latest version

        :parm package: The name of the package or Gitlab URL
        :returns: A tuple of the name and version specs for the package
        :raises QipError: if there was an error queriying pip for the
                          latest version information if no spec is
                          included with the ``package`` parm
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

    def parse_dependencies(self, deps):
        """
        Strips out the package name of the dependencies from the pip
        output
        """
        out_deps = []
        for line in deps.split("\n"):
            if line.startswith("Collecting"):
                out_deps.append(line.split()[1])
        return out_deps

    def fetch_dependencies(self, package, deps_install):
        """
        Recursively fetch dependencies for *package*. Populates the
        *deps_install* dictionary passed to it with the package name
        and version specs {name: specs}. *deps_install* is a `dict` that
        will be populated with the package details to install later.

        :param package: The package name for which to get dependecies
        :param deps_install: List of the dependencies to install later
        :raises QipError: If the pip query for dependencies fails
        """
        cmd = (
            "download --exists-action w '{0}' "
            "-d /tmp --no-binary :all:"
            .format(package)
        )

        output, stderr, exit_code = self.run_pip(cmd)
        if exit_code != 0:
            raise QipError("{}\n{}".format(output, stderr))

        deps = self.parse_dependencies(output)
        deps.remove("{}".format(package))

        m = re.search(r"\/(\w+)\.git.*$", package)
        if m:
            cur_name = m.group(1)
        else:
            cur_name = Req.parse(package).unsafe_name

        self.dependency_tracker[cur_name] = {"deps": [],
                                             "path": ""}
        for dep in deps:
            pkg_req = Req.parse(dep)
            name = pkg_req.unsafe_name
            specs = pkg_req.specs
            self.dependency_tracker[cur_name]["deps"].append({name: ""})
            if name in deps_install.keys():
                self.logger.info("\tSkipping {}. Already satisfied. "
                                 .format(name))
                continue
            deps_install[name] = specs
            self.fetch_dependencies(dep, deps_install)

    def install_package(self, package, spec, overwrite=False):
        """
        Install a *package* of *spec*.

        :param package: Name of package to install
        :param spec: The standard version spec string for the package to
                     install as a string
        :param overwrite: Boolean to indicate whether to automatically
                          overwrite the package if it already exists at the
                          output directory.
        :returns: a tuple of the command output and return code

        :raises QipError: if it is unable to create target directory
        :raises QipPackageInstalled: if the package is already installed and
                                     overwrite is ``False``
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
                _, _, exit_status = self.run_cmd("mkdir -p -m 755 {}"
                                                 .format(outdir))
                if exit_status != 0:
                    raise QipError("Unable to create install "
                                   "directory: {}", outdir)

                install_target = os.path.join(outdir, m.group(1))
                if os.path.isdir(install_target) and not overwrite:
                    ex = QipPackageInstalled("Package {} already "
                                             "installed to index."
                                             .format(m.group(1)))
                    ex.target_dir = install_target
                    raise ex

                self.install(temp_dir, install_target)
                try:
                    self.set_dependecies(package, install_target)
                except KeyError:
                    # We are not installing dependencies so no need to set
                    # them
                    pass

            return output, ret_code
        finally:
            if temp_dir:
                self.rmtree(temp_dir)

    def set_dependecies(self, package, target):
        """
        Set the dependencies into a dictionary which will get dumped to a
        json file as the requirements for a given package

        Its structure is:

        .. code:: python

            {u'Jinja2': {'deps': [{u'MarkupSafe': u'/tmp/installs/MarkupSafe/MarkupSafe-1.0'}],
                         'path': u'/tmp/installs/Jinja2/Jinja2-2.10'},
             u'MarkupSafe': {'deps': [],
                             'path': u'/tmp/installs/MarkupSafe/MarkupSafe-1.0'},
             u'Werkzeug': {'deps': [], 'path': u'/tmp/installs/Werkzeug/Werkzeug-0.14.1'},
             u'click': {'deps': [], 'path': u'/tmp/installs/click/click-6.7'},
             u'flask': {'deps': [{u'Werkzeug': u'/tmp/installs/Werkzeug/Werkzeug-0.14.1'},
                                 {u'Jinja2': u'/tmp/installs/Jinja2/Jinja2-2.10'},
                                 {u'itsdangerous': u'/tmp/installs/itsdangerous/itsdangerous-0.24'},
                                 {u'click': u'/tmp/installs/click/click-6.7'},
                                 {u'MarkupSafe': u'/tmp/installs/MarkupSafe/MarkupSafe-1.0'}],
                         'path': u'/tmp/installs/flask/flask-1.0.2'},
             u'itsdangerous': {'deps': [],
                               'path': u'/tmp/installs/itsdangerous/itsdangerous-0.24'}}

        """
        self.dependency_tracker[package]["path"] = target
        for k, v in self.dependency_tracker.iteritems():
            for i, dep in enumerate(v["deps"]):
                if dep.get(package) is not None:
                    self.dependency_tracker[k]["deps"][i][package] = target

    def strip_output(self, stdout, stderr):
        # Strip shell colour code characters
        ansi_escape = re.compile(
            r'\x1B\[[0-?]*[ -/]*[@-~]', re.IGNORECASE | re.MULTILINE
        )

        stdout = ''.join(stdout)
        stdout = ansi_escape.sub('', stdout)

        stderr = ''.join(stderr)
        stderr = ansi_escape.sub('', stderr)

        return stdout, stderr

    def run_pip(self, cmd):
        """
        Execute pip in a wiz context ensuring the right version of pip
        is called in the correct environment

        :parm cmd" the command to execute without a `pip` prefix
        :returns: stdout, stderr, and exit status of command
        """
        cmd = "pip {}".format(cmd)
        context = wiz.resolve_context(["python==2.7.*"])
        stdout, stderr, exit_status = self.run_cmd(cmd, context["environ"])
        return stdout, stderr, exit_status

    def install(self, from_dir, to_dir):
        """
        install a package by syncing the temporary install dir to the
        correct directory structure under ``output directory``

        :parm from_dir: string of the temporary directory to copy from
        :parm to_dir: target to copy to. Must exist before calling this method
        """
        cmd = "rsync -azvl {0}/ {1}".format(from_dir, to_dir)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def mkdtemp(self, path):
        """
        Create a temporary directory under path with a uuid.
        Caller is responsible for deleting temporary directory

        :parm path: the root path under which to create the temp dir
        :returns: tuple of full path to temporary direcory and exitstatus
                  of mkdir command.
        """
        _file = os.path.join(path, "tmp" + uuid.uuid4().hex)
        _, _, exit_status = self.run_cmd("mkdir -m 755 {}".format(_file))
        return _file, exit_status

    def rmtree(self, path):
        """
        Recursively delete a folder and all its subfolders

        :parm path: folder to delete
        :returns: stdout, stderr, and exit_status of rm command
        """
        cmd = "rm -rf {}".format(path)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def run_cmd(self, cmd, env=None):
        """
        Run a command via subprocess.Popen and return its stdout, stderr and
        return code. Strips all control characters from streams.

        :parm cmd: the command to execute and its arguments as a string
        :parm env: the environment to execute the command in

        :returns: stdout, stderr, and exit status of command
        """
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
