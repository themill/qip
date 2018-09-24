# :coding: utf-8

import os
import pytest
import shutil
import getpass
import re

from click.testing import CliRunner

from qip.command_line import install


def strip_output(text):
        # Strip shell colour code characters
        ansi_escape = re.compile(
            r'\x1B\[[0-?]*[ -/]*[@-~]', re.IGNORECASE | re.MULTILINE
        )
        text = u''.join(text)
        text = ansi_escape.sub('', text)
        return text


def test_without_arguments():
    """Command without arguments prints missing package error."""
    runner = CliRunner()
    result_help = ("Usage: install [OPTIONS] PACKAGE\n\n"
                   "Error: Missing argument \"package\".\n")

    result = runner.invoke(
        install, input='\ry\n'
    )
    assert result.exit_code == 2
    assert result.exception
    assert result.output == result_help


def test_missing_output():
    """Error when user does not specify and output directory"""
    runner = CliRunner()
    result = runner.invoke(install, ['test'])
    assert result.exit_code == 1
    assert result.exception
    assert strip_output(result.output) == "error: Please specify an output directory.\n"


def test_fail_missing_version():
    runner = CliRunner()
    result = runner.invoke(install, ['-o /tmp/test', 'git@gitlab:rnd/mlog.git'])
    assert result.exit_code == 1
    assert result.exception


def test_fail_wrong_version():
    runner = CliRunner()
    result = runner.invoke(install, ['-o /tmp/test', 'git@gitlab:rnd/mlog.git@999999'])
    assert result.exit_code == 1
    assert result.exception
