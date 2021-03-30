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
    "coloredlogs >= 14.0, < 15",
    "colorama >= 0.3.9, < 1",
    "distro >= 1.5.0, < 2",
    "packaging >= 17.1, < 18",
    "pip >= 10",
    "six >= 1.15.0, < 2",
    "wiz-env >= 3, < 4"
]
DOC_REQUIRES = [
    "sphinx >= 1.8, < 2",
    "sphinx_rtd_theme >= 0.1.6, < 1",
    "lowdown >= 0.1.0, < 2",
    "sphinx-click >= 1.2.0"
]
TEST_REQUIRES = [
    "pytest >= 4, < 5",
    "pytest-cov >= 2, < 3",
    "pytest-mock >= 1, < 2",
    "pytest-runner >= 2.7, < 3",
    "pytest-xdist >= 1.18, < 2"
]

setup(
    name="qip-installer",
    version=VERSION,
    description="Quarantined Installer for Python",
    long_description=open(README_PATH).read(),
    url="https://github.com/themill/qip",
    keywords="",
    author="The Mill",
    packages=find_packages(SOURCE_PATH),
    package_dir={
        "": "source",
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "doc": DOC_REQUIRES,
        "test": TEST_REQUIRES,
        "dev": DOC_REQUIRES + TEST_REQUIRES
    },
    python_requires=(
        ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5*"
    ),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "qip = qip.__main__:main"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 "
        "(LGPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development",
    ],
)
