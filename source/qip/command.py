# :coding: utf-8

import subprocess
import shlex

import qip.logging


def execute(command, environ_mapping, quiet=False):
    """Execute *command* within *environ_mapping*.

    :param command: command to execute.

        It should be in the form of::

            "pip install foo"

    :param environ_mapping: mapping with all environment variables that
        must be set for the *command* to run properly.
    :param quiet: indicate whether output lines should be hidden.
        Default is False.

    :raise RuntimeError: if command execution fails

    :return: Command output.

    """
    logger = qip.logging.Logger(__name__ + ".execute")
    logger.debug(command)

    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environ_mapping
    )

    if not quiet:
        output = ""

        lines_iterator = iter(process.stdout.readline, b"")
        while process.poll() is None:
            for line in lines_iterator:
                output += str(line)
                _line = line.rstrip()
                logger.debug(_line.decode("latin"))

        stderr = "\n".join(process.stderr.readlines())
    else:
        output, stderr = process.communicate()

    if len(stderr):
        raise RuntimeError(stderr)

    return output
