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
            stdout, stderr, exit_status = self.run_remote_cmd("{} {} {}".format(cmd, "700", file))

            return file

    def rename_dir(self, from_dir, to_dir):
        cmd = "sudo -u admin3d mv {} {}".format(from_dir, to_dir)
        stdout, stderr, exit_status = self.run_remote_cmd(cmd)
        return stdout, stderr, exit_status

    def rmtree(self, dir):
        cmd = "sudo -u admin3d rm -rf {}".format(dir)
        stdout, stderr, exit_status = self.run_remote_cmd(cmd)
        return stdout, stderr, exit_status

    def run_remote_pip(self, cmd):
        cmd = re.sub(r'^pip\b', self.pipcmd, cmd)
        cmd = "sudo -u admin3d {}".format(cmd)
        self.ctx.printer.debug("Running {0} on {1}".format(cmd, self.target))
        stdout, stderr, exit_status = self.run_remote_cmd(cmd)

        return stdout, stderr, exit_status

    def run_remote_cmd(self, cmd):
        username = getpass.getuser()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(self.target, username=username, password=self.password)

        self.ctx.printer.debug("Running {0} on {1}".format(cmd, self.target))
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=True)

        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]',
                                 re.IGNORECASE | re.MULTILINE)
        outlines = ssh_stdout.readlines()
        stdout = ''.join(outlines)
        stdout = ansi_escape.sub('', stdout)

        stderr = ssh_stderr.readlines()
        stderr = ''.join(outlines)
        stderr = ansi_escape.sub('', stderr)

        exit_status = ssh_stdout.channel.exit_status
        ssh.close()

        self.ctx.printer.debug("Command returned: {0} :: {1} [{2}]".format(
                                stdout, stderr, exit_status))

        return stdout, stderr, exit_status