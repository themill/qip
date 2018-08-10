# :coding: utf-8

import paramiko
import getpass
import subprocess
import re
import tempfile
import os


class CmdRunner(object):
    def __init__(self, target, password, logger):
        self.cmd = RemoteCmd(target, password, logger)
        if target['server'] is 'localhost':
            self.cmd = LocalCmd(target, password, logger)

    def __getattr__(self, attr):
        try:
            return getattr(self.cmd, attr)
        except AttributeError:
            # If attribute was not found in self.cmd, then try in self
            return object.__getattribute__(self, attr)


class Command(object):
    def __init__(self, target, password, logger):
        self.target = target
        self.password = password
        self.logger = logger

    def strip_output(self, stdout, stderr):
        # Strip shell colour code characters
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]',
                                 re.IGNORECASE | re.MULTILINE)
        stdout = u''.join(stdout)
        stdout = ansi_escape.sub('', stdout)

        stderr = u''.join(stderr)
        stderr = ansi_escape.sub('', stderr)

        return stdout, stderr

    def mkdtemp(self, path=None):
        names = tempfile._get_candidate_names()

        # for seq in range(tempfile.TMP_MAX):
        name = next(names)
        if path is None:
            path = self.target["install_dir"]

        file = os.path.join(path, "tmp" + name)

        cmd = "mkdir -m"
        _, _, exit_status = self.run_cmd("{} {} {}".format(cmd, "755", file))

        return file, exit_status

    def install_and_sync(self, from_dir, to_dir):
        if to_dir.startswith('/mill3d/server/apps'):
            for loc, server in self.ctx.cfg['LOCATION_LUT'].iteritems():
                cmd = ("rsync -azvl {0}/ {2}:{1}"
                       .format(from_dir, to_dir, server))

                stdout, stderr, exit_status = self.run_cmd(cmd)
                if exit_status != 0:
                    self.ctx.mlogger.error("Sync to {} failed with error: {}\n"
                                           "Carrying on with other servers."
                                           .format(server, stderr))
        else:
            cmd = "rsync -azvl {0}/ {1}".format(from_dir, to_dir)
            stdout, stderr, exit_status = self.run_cmd(cmd)

    def rmtree(self, path):
        cmd = "rm -rf {}".format(path)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def run_pip(self, cmd):
        cmd = re.sub(r'^pip\b', self.target["pipcmd"], cmd)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def run_cmd(self, cmd):
        raise NotImplementedError


class RemoteCmd(Command):
    def __init__(self, target, password, logger):
        super(RemoteCmd, self).__init__(target, password, logger)

    def run_cmd(self, cmd):
        username = getpass.getuser()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.target["server"], username=username,
                        password=self.password)
        except paramiko.ssh_exception.AuthenticationException:
            self.logger.error("Unable to connect to {} as {}."
                              .format(self.target["server"], username))
            raise

        cmd = "sudo -u admin3d {}".format(cmd)

        self.logger.debug("Running {0} on {1}"
                          .format(cmd, self.target["server"]))
        _, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

        stdout, stderr = self.strip_output(ssh_stdout.readlines(),
                                           ssh_stderr.readlines())

        exit_status = ssh_stdout.channel.recv_exit_status()
        ssh.close()

        self.logger.debug(u"Command returned: \n"
                          "STDOUT: {0}\n"
                          "STDERR: {1}\n"
                          "Exit Code: {2}"
                          .format(stdout, stderr, exit_status))

        return stdout, stderr, exit_status


class LocalCmd(Command):
    def __init__(self, target, password, logger):
        super(LocalCmd, self).__init__(target, password, logger)

    def run_cmd(self, cmd):
        self.logger.debug("Running {0} on {1}".
                          format(cmd, self.target["server"]))

        ps = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
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
