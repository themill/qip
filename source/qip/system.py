# :coding: utf-8

import platform as _platform

import distro
from packaging.version import Version, InvalidVersion


def query():
    """Return system mapping.

    :raise RuntimeError: if platform is not supported.

    :return: system mapping.

     It should be in the form of::

        {
            "platform": "linux",
            "arch": "x86_64",
            "os": {
                "name": "centos",
                "major_version": 7
            }
        }

    """
    name = _platform.system().lower()

    try:
        if name == "linux":
            mapping = query_linux()
        elif name == "darwin":
            mapping = query_mac()
        elif name == "windows":
            mapping = query_windows()
        else:
            raise RuntimeError

    except InvalidVersion as error:
        raise RuntimeError(
            "The operating system version found seems incorrect [{}]".format(
                error
            )
        )

    return mapping


def query_linux():
    """Return Linux system mapping.

    :return: system mapping.

    """
    distribution, version, _ = distro.linux_distribution(
        full_distribution_name=False
    )

    return {
        "platform": "linux",
        "arch": _platform.machine(),
        "os": {
            "name": distribution,
            "major_version": _extract_major_version(version)
        }
    }


def query_mac():
    """Return mac system mapping.

    :return: system mapping.

    """
    return {
        "platform": "mac",
        "arch": _platform.machine(),
        "os": {
            "name": "mac",
            "major_version": _extract_major_version(_platform.mac_ver()[0])
        }
    }


def query_windows():
    """Return windows system mapping.

    .. warning::

        The Windows versions superior to 8 will not be recognised properly with
        a Python version under 2.7.11

        https://hg.python.org/cpython/raw-file/53d30ab403f1/Misc/NEWS

        Also a bug as been introduced in Python 2.7.11 that prevent the
        recognition of old Windows version

        https://bugs.python.org/issue26513

    :return: system mapping.

    """
    return {
        "platform": "windows",
        "arch": _platform.machine(),
        "os": {
            "name": "windows",
            "major_version": _extract_major_version(_platform.win32_ver()[1])
        }
    }


def _extract_major_version(version):
    """Extract major version of operating system request for *version*.

    :param version: Version instance.

    :return: Major version integer.

    """
    version = Version(version)
    return int(version.base_version.split(".", 1)[0])
