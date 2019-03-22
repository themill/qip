# :coding: utf-8

import os
import re

from setuptools import setup, find_packages


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
RESOURCE_PATH = os.path.join(ROOT_PATH, "resource")
SOURCE_PATH = os.path.join(ROOT_PATH, "source")
README_PATH = os.path.join(ROOT_PATH, "README.rst")

PACKAGE_NAME = "qip"

# Read version from source.
with open(
    os.path.join(SOURCE_PATH, PACKAGE_NAME, "_version.py")
) as _version_file:
    VERSION = re.match(
        r".*__version__ = \"(.*?)\"", _version_file.read(), re.DOTALL
    ).group(1)


# Compute dependencies.
INSTALL_REQUIRES = [
    "click >= 7, < 8",
    "mlog >= 0.0.6, < 1",
    "packaging >= 17.1, < 18",
    "pip >= 10, < 19",
    "wiz >= 2, < 3"
]
DOC_REQUIRES = [
    "sphinx >= 1.2.2, < 2",
    "sphinx_rtd_theme >= 0.1.6, < 1",
    "lowdown >= 0.1.0, < 2",
    "sphinx-click>=1.2.0",
]
TEST_REQUIRES = [
    "mock >= 2, < 3",
    "pytest-runner >= 2.7, < 3",
    "pytest >= 3.0.0, < 4",
    "pytest-mock >= 0.11, < 1",
    "pytest-xdist >= 1.1, < 2",
    "pytest-cov >= 2, < 3",

    # Ensure that more-itertools is limited to v6 as later version don't work
    # for python 2.7.
    "more-itertools >= 4, < 6"
]

setup(
    name="qip",
    version=VERSION,
    description="Quarantined Installer for Python",
    long_description=open(README_PATH).read(),
    url="http://gitlab/rnd/qip",
    keywords="",
    author="The Mill",
    packages=find_packages(SOURCE_PATH),
    package_dir={
        "": "source",
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TEST_REQUIRES,
    extras_require={
        "doc": DOC_REQUIRES,
        "test": TEST_REQUIRES,
        "dev": DOC_REQUIRES + TEST_REQUIRES
    },
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "qip = qip.__main__:main"
        ]
    },
)
