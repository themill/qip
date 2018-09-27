# :coding: utf-8

from __future__ import print_function
import subprocess
import shlex

import mlog


def execute(command, environ_mapping, quiet=False):
    """Execute *command* within *environ_mapping*.

    * *command* should be in the form of::

        "pip install foo"

    * *environ_mapping* should be a mapping with all environment variables which
      must be set for the *command* to run properly.
    * *quiet* indicate whether output lines should be hidden. Default is False.

    """
    logger = mlog.Logger(__name__ + ".execute")
    logger.debug(command)

    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environ_mapping
    )

    output = None

    if not quiet:
        output = []

        lines_iterator = iter(process.stdout.readline, b"")
        while process.poll() is None:
            for line in lines_iterator:
                output.append(line)
                _line = line.rstrip()
                print(_line.decode("latin"), end="\n")

    errors = process.stderr.readlines()
    if len(errors):
        raise RuntimeError("".join(errors))

    return "".join(output or process.stdout.readlines())
