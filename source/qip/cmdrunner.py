# :coding: utf-8

import paramiko
import getpass
import subprocess
import re
import shutil
import tempfile
import platform
import os
import sys


class CmdRunner(object):
    def __init__(self, ctx):
        self.cmd = RemoteCmd(ctx)
        if ctx.target['server'] is 'localhost':
            self.cmd = LocalCmd(ctx)

    def __getattr__(self, attr):
        try:
            return getattr(self.cmd, attr)
        except AttributeError:
            # If attribute was not found in self.cmd, then try in self
            return object.__getattr__(self, attr)


class Command(object):
    def __init__(self, ctx):
        self.target = ctx.target
        self.ctx = ctx
        self.password = ctx.password

    def strip_output(self, stdout, stderr):
        # Strip shell colour code characters
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]',
                                 re.IGNORECASE | re.MULTILINE)
        stdout = u''.join(stdout)
        stdout = ansi_escape.sub('', stdout)

        stderr = u''.join(stderr)
        stderr = ansi_escape.sub('', stderr)

        return stdout, stderr

    def mkdtemp(self, dir=None):
        names = tempfile._get_candidate_names()

        # for seq in range(tempfile.TMP_MAX):
        name = next(names)
        if dir is None:
            dir = self.target["install_dir"]

        file = os.path.join(dir, "tmp" + name)

        cmd = "mkdir -m"
        _, _, exit_status = self.run_cmd("{} {} {}".format(cmd, "755", file))

        return file, exit_status

    def rename_dir(self, from_dir, to_dir):
        cmd = "mv {} {}".format(from_dir, to_dir)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def rmtree(self, dir):
        cmd = "rm -rf {}".format(dir)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def run_pip(self, cmd):
        cmd = re.sub(r'^pip\b', self.target["pipcmd"], cmd)
        stdout, stderr, exit_status = self.run_cmd(cmd)

        return stdout, stderr, exit_status

    def run_cmd(self, cmd):
        raise NotImplementedError


class RemoteCmd(Command):
    def __init__(self, ctx):
        super(RemoteCmd, self).__init__(ctx)

    def run_cmd(self, cmd):
        username = getpass.getuser()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.target["server"], username=username, password=self.password)
        except paramiko.ssh_exception.AuthenticationException:
            self.ctx.printer.error("Unable to connect to {} as {}."
                                   .format(self.target["server"], username))
            sys.exit(1)

        cmd = "sudo -u admin3d {}".format(cmd)

        self.ctx.printer.debug("Running {0} on {1}".format(cmd, self.target["server"]))
        _, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)#, get_pty=True)

        stdout, stderr = self.strip_output(ssh_stdout.readlines(), ssh_stderr.readlines())

        exit_status = ssh_stdout.channel.recv_exit_status()
        ssh.close()

        self.ctx.printer.debug(u"Command returned: \n"
                               "STDOUT: {0}\n"
                               "STDERR: {1}\n"
                               "Exit Code: {2}".format(
                                stdout, stderr, exit_status))

        return stdout, stderr, exit_status


class LocalCmd(Command):
    def __init__(self, ctx):
        super(LocalCmd, self).__init__(ctx)

        distro = platform.release()
        distro = "-".join(distro.split('.')[-2:]).replace('_', '-')
        for k, v in self.target.iteritems():
            self.target[k] = v.replace('{{platform}}', distro)

    def run_cmd(self, cmd):
        self.ctx.printer.debug("Running {0} on {1}".format(cmd, self.target["server"]))

        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = ps.communicate()

        stdout, stderr = self.strip_output(stdout, stderr)

        self.ctx.printer.debug(u"Command returned: \n"
                               "STDOUT: {0}\n"
                               "STDERR: {1}\n"
                               "Exit Code: {2}".format(
                                stdout, stderr, ps.returncode))

        return stdout, stderr, ps.returncode
