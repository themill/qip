# :coding: utf-8

import collections
import getpass
import logging
import logging.config
import os
import sys
import tempfile

import coloredlogs
import wiz.filesystem

# Configure custom colors for messages displayed in the console.
coloredlogs.DEFAULT_LEVEL_STYLES = {
    "info": {"color": "cyan"},
    "error": {"color": "red"},
    "critical": {"color": "red"},
    "warning": {"color": "yellow"}
}

#: Available levels with corresponding labels.
LEVEL_MAPPING = collections.OrderedDict([
    ("debug", logging.DEBUG),
    ("info", logging.INFO),
    ("warning", logging.WARNING),
    ("error", logging.ERROR),
])

#: Output path for files exported by default 'file' handler.
PATH = os.path.join(tempfile.gettempdir(), "qip", "logs")


def initiate(console_level="info"):
    """Initiate logger configuration.

    :param console_level: Initialize the logging level for the console handler
        if possible. Default is "info".

    """
    # Ensure that default output path exists.
    wiz.filesystem.ensure_directory(PATH)

    logging.config.dictConfig({
        "version": 1,
        "root": {
            "handlers": ["console", "file"],
            "level": logging.DEBUG
        },
        "formatters": {
            "standard": {
                "class": "coloredlogs.ColoredFormatter",
                "format": "%(message)s"
            },
            "detailed": {
                "class": "logging.Formatter",
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
                "level": LEVEL_MAPPING[console_level]
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "level": logging.INFO,
                "filename": os.path.join(
                    PATH, "{}.log".format(getpass.getuser())
                ),
                "maxBytes": 10485760,
                "backupCount": 20,
            }
        }
    })

    # Formatter class cannot be initiate via config in Python 2.7.
    if sys.version_info[0] < 3:
        coloredlogs.install(
            fmt="%(message)s",
            stream=sys.stdout,
            level=console_level.upper(),
        )
