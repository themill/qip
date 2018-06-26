from pkg_resources import Requirement as Req
import click
import os
import re

class Qip(object):
    def __init__(self, ctx, runner):
        self.ctx = ctx
        self.runner = runner

    def download_package(self, package, spec):
        """
        Download *package* with *spec* from Pypi or gitlab. Returns
        *False* if unable to do so, and *True* if successful.
        """

        cmd = ("pip download --no-deps --exists-action a "
            "--dest {0} --no-cache --find-links {0}".format(self.ctx.target["package_idx"])
            )

        if not spec:
            spec = ''
        cmd += " '{}{}'".format(package, spec)
        self.ctx.printer.status("Downloading {0} {1}".format(package, spec))
        output, stderr, ret_code = self.runner.run_pip(cmd)

        if output.split('\n')[1].strip().startswith('File was already downloaded'):
            self.ctx.printer.info("{0}".
                            format(output.split('\n')[1].strip()))
            self.ctx.printer.status("Download skipped.")
            return True

        if ret_code != 0:
            self.ctx.printer.error("Unable to download requested package. Reason from pip below")
            self.ctx.printer.error(stderr)
            self.ctx.printer.warning("If this is a package from Gitlab you should download it first.")
            return False

        self.ctx.printer.status("Package {0} {1} downloaded.".format(package, spec))
        return True

    def get_name_and_specs(self, package):
        specs = []
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
                                " {0} '{1}=='".format(self.ctx.target["package_idx"], name))
                output, stderr, ret_code = self.runner.run_pip(test_cmd)
                match = re.search(r"\(from versions: ((.*))\)", output[1])
                if match:
                    version = match.group(1).split(", ")[-1]
                    specs = [('==', version)]

        return name, specs

    def fetch_dependencies(self, package, deps_install):
        """
        Recursively fetch dependencies for *package*. Populates the
        *deps_install* dictionary passed to it with the package name
        and version specs [name: specs]
        """
        self.ctx.printer.status("Resolving deps for {}".format(package))
        cmd = ("pip download --exists-action w '{0}' "
            "-d /tmp --no-binary :all: --find-links {1} --no-cache"
            "| grep Collecting | cut -d' ' "
            "-f2 | grep -v '{0}'".format(package, self.ctx.target["package_idx"]))
        output, stderr, _ = self.runner.run_pip(cmd)
        deps = output.split()

        for dep in deps:
            pkg_req = Req.parse(dep)
            name = pkg_req.unsafe_name
            specs = pkg_req.specs
            if name in deps_install.keys():
                self.ctx.printer.info("\tSkipping {}. Already processed. ".format(name))
                continue
            deps_install[name] = specs
            self.fetch_dependencies(dep, deps_install)

    def install_package(self, package, version, download=False):
        """
        Install a *package* of *version*. If download is *True* will
        automatically download the package first, otherwise will prompt
        to download
        """
        spec = ','.join( (ver[0] + ver[1] for ver in version) )
        self.ctx.printer.status("Installing {} : {}".format(package, spec))
        temp_dir = None

        # Need this to catch hard exists and clean up temp dir
        try:
            temp_dir, exit_status = self.runner.mkdtemp()
            if exit_status != 0:
                self.ctx.printer.error("Unable to create temp directory")
                sys.exit(1)

            cmd = ("pip install --ignore-installed --no-deps --prefix {0}"
                " --no-index --no-cache-dir --find-links {1}"
                " '{2}{3}'".format(temp_dir, self.ctx.target['package_idx'], package, spec)
                )

            output, stderr, ret_code = self.runner.run_pip(cmd)

            if ret_code == 1:
                if not download and not self.check_to_download(package, stderr):
                    self.ctx.printer.warning("Not downloading {}. "
                                             "Skipping installation.".format(package))
                else:
                    if not self.download_package(package, spec):
                        self.runner.rmtree(temp_dir)
                        return "", 1
                    self.install_package(package, version)
            else:
                lastline = output.split('\n')[-2].strip()
                m = re.search(r'(\S+-[\d\.]+)$', lastline)
                if m:
                    if os.path.isdir("{0}/{1}".format(self.ctx.target['install_dir'],
                                                      m.group(1))):
                        self.ctx.printer.warning("Package {} already exists in index."
                                                 .format(m.group(1)))
                        if not click.confirm("Overwrite it?"):
                            self.runner.rmtree(temp_dir)
                            return "", 1
                    try:
                        self.runner.rename_dir(temp_dir,
                                        "{0}/{1}".format(self.ctx.target['install_dir'], m.group(1)))
                    except OSError:
                        self.runner.rmtree(temp_dir)
            return output, ret_code
        finally:
            if temp_dir:
                self.runner.rmtree(temp_dir)

    def check_to_download(self, package, output):
        """
        Confirmation prompt if the requested *package* is not found. Parses
        *output* to see if packge is missing. Returns *True* if user wishes
        to download the package, *False* otherwise
        """
        if output.split('\n')[-2].startswith("No matching distribution found for"):
            self.ctx.printer.warning("{0} not found in package index.".format(package))
            return click.confirm('Do you want to try and download it now?')
        return False