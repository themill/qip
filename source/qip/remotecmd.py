import paramiko
import getpass
import subprocess
import re
import shutil
import tempfile
import platform
import os

class CmdRunner(object):
    def __init__(self, ctx, target, password):
        self.cmd = RemoteCmd(ctx, target, password)
        if target['server'] is 'localhost':
            self.cmd = LocalCmd(ctx, target, password)

    def __getattr__(self, attr):
        try:
            return getattr(self.cmd, attr)
        except AttributeError:
            #If attribute was not found in self.df, then try in self
            return object.__getattr__(self, attr)


class RemoteCmd(object):
    def __init__(self, ctx, target, password):
        self.target = target
        self.ctx = ctx
        self.password = password

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

        #for seq in range(tempfile.TMP_MAX):
        name = next(names)
        if dir is None:
            dir = self.target["install_dir"]

        file = os.path.join(dir, "tmp" + name)

        cmd = "sudo -u admin3d mkdir -m"
        stdout, stderr, exit_status = self.run_cmd("{} {} {}".format(cmd, "755", file))

        return file, exit_status

    def rename_dir(self, from_dir, to_dir):
        cmd = "sudo -u admin3d mv {} {}".format(from_dir, to_dir)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def rmtree(self, dir):
        cmd = "sudo -u admin3d rm -rf {}".format(dir)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def run_pip(self, cmd):
        cmd = re.sub(r'^pip\b', self.target["pipcmd"], cmd)
        cmd = "sudo -u admin3d {}".format(cmd)
        stdout, stderr, exit_status = self.run_cmd(cmd)

        return stdout, stderr, exit_status

    def run_cmd(self, cmd):
        username = getpass.getuser()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(self.target["server"], username=username, password=self.password)

        self.ctx.printer.debug("Running {0} on {1}".format(cmd, self.target["server"]))
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)#, get_pty=True)

        stdout, stderr = self.strip_output(ssh_stdout.readlines(), ssh_stderr.readlines())

        exit_status = ssh_stdout.channel.recv_exit_status()
        ssh.close()

        self.ctx.printer.debug(u"Command returned: \n"
                               "STDOUT: {0}\n"
                               "STDERR: {1}\n"
                               "Exit Code: {2}".format(
                                stdout, stderr, exit_status))

        return stdout, stderr, exit_status


class LocalCmd(RemoteCmd):
    def __init__(self, ctx, target, password):
        super(LocalCmd, self).__init__(ctx, target, password)

        distro = platform.release()
        distro = ('-').join(distro.split('.')[-2:]).replace('_', '-')
        for k, v in self.target.iteritems():
            self.target[k] = v.replace('{{platform}}', distro)