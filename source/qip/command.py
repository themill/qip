# :coding: utf-8

import logging
import shlex
import subprocess


def execute(command, environ_mapping, quiet=False):
    """Execute *command* within *environ_mapping*.

    :param command: command to execute.

        It should be in the form of::

            "python -m pip install foo"

    :param environ_mapping: mapping with all environment variables that
        must be set for the *command* to run properly.
    :param quiet: indicate whether output lines should be hidden.
        Default is False.

    :raise RuntimeError: if command execution fails

    :return: Command output.

    """
    logger = logging.getLogger(__name__ + ".execute")
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
                output += line.decode("utf-8")
                _line = line.rstrip().decode("utf-8")
                logger.debug(_line)

        stderr = b"\n".join(process.stderr.readlines()).decode("utf-8")
    else:
        output, stderr = process.communicate()

        # Decode process output for display
        output = output.decode("utf-8")
        stderr = stderr.decode("utf-8")

    if len(stderr):
        raise RuntimeError(stderr)

    return output
