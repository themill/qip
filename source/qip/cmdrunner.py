# :coding: utf-8

import subprocess
import re
import uuid
import os
import wiz


class LocalCmd(object):
    def __init__(self, logger):
        self.logger = logger

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

    def mkdtemp(self, path):
        tmp_path = os.path.join(path, "qip_tmp" + uuid.uuid4().hex)
        _, _, exit_status = self.run_cmd("mkdir -pm 755 {}".format(tmp_path))
        return tmp_path, exit_status

    def rmtree(self, path):
        cmd = "rm -rf {}".format(path)
        stdout, stderr, exit_status = self.run_cmd(cmd)
        return stdout, stderr, exit_status

    def run_pip(self, cmd):
        cmd = "pip {}".format(cmd)
        context = wiz.resolve_context(["python==2.7.*"])
        stdout, stderr, exit_status = self.run_cmd(cmd, context["environ"])
        return stdout, stderr, exit_status

    def install(self, from_dir, to_dir):
        cmd = "rsync -azvl {0}/ {1}".format(from_dir, to_dir)
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
