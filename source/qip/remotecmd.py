import paramiko
import getpass
import subprocess
import re
import tempfile
import os

class RemoteCmd(object):
    def __init__(self, ctx, cfg, target, password):
        self.cfg = cfg
        self.target = cfg['TARGETS'][target]
        self.pipcmd = cfg['PIP_CMDS'][target]
        self.ctx = ctx
        self.password = password

    def mkdtemp(self, dir):
        names = tempfile._get_candidate_names()

        for seq in range(tempfile.TMP_MAX):
            name = next(names)
            file = os.path.join(dir, "tmp" + name)

            cmd = "sudo -u admin3d mkdir -m"
            stdout, stderr = self.run_remote_cmd("{} {} {}".format(cmd, "700", file))
            print stdout, stderr

            return file

    def rename_dir(self, from_dir, to_dir):
        cmd = "sudo -u admin3d mv {} {}".format(from_dir, to_dir)
        stdout, stderr = self.run_remote_cmd(cmd)
        print stdout, stderr
        return stdout, stderr

    def run_remote_pip(self, cmd):
        cmd = re.sub(r'^pip\b', self.pipcmd, cmd)
        cmd = "sudo -u admin3d {}".format(cmd)
        self.ctx.printer.debug("Running {0} on {1}".format(cmd, self.target))
        stdout, stderr = self.run_remote_cmd(cmd)

        return stdout, 01

    def run_remote_cmd(self, cmd):
        username = getpass.getuser()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(self.target, username=username, password=self.password)

        self.ctx.printer.debug("Running {0} on {1}".format(cmd, self.target))
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)

        outlines = ssh_stdout.readlines()
        stdout = ''.join(outlines)
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]',
                                 re.IGNORECASE | re.MULTILINE)
        stdout = ansi_escape.sub('', stdout)

        stderr = ssh_stderr.readlines()
        print stderr

        #stderr = '\n'.join(outlines)
        ssh.close()

        self.ctx.printer.debug("Command returned: {0} :: {1}".format(
                                stdout, stderr))

        return stdout, stderr