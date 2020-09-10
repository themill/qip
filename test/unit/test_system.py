# :coding: utf-8

import platform

import distro
import pytest
from packaging.version import InvalidVersion

import qip.system


@pytest.fixture()
def mocked_platform_system(mocker):
    """Mocked the platform.system function."""
    return mocker.patch.object(platform, "system")


@pytest.fixture()
def mocked_platform_machine(mocker):
    """Mocked the platform.machine function."""
    return mocker.patch.object(platform, "machine")


@pytest.fixture()
def mocked_platform_linux(mocker):
    """Mocked the distro.linux_distribution function."""
    return mocker.patch.object(distro, "linux_distribution")


@pytest.fixture()
def mocked_platform_mac(mocker):
    """Mocked the platform.mac_ver function."""
    return mocker.patch.object(platform, "mac_ver")


@pytest.fixture()
def mocked_platform_win32(mocker):
    """Mocked the platform.win32_ver function."""
    return mocker.patch.object(platform, "win32_ver")


@pytest.fixture()
def mocked_query_linux(mocker):
    """Mocked the query_linux function."""
    return mocker.patch.object(
        qip.system, "query_linux", return_value="LINUX_SYSTEM_MAPPING"
    )


@pytest.fixture()
def mocked_query_mac(mocker):
    """Mocked the query_mac function."""
    return mocker.patch.object(
        qip.system, "query_mac", return_value="MAC_SYSTEM_MAPPING"
    )


@pytest.fixture()
def mocked_query_windows(mocker):
    """Mocked the query_windows function."""
    return mocker.patch.object(
        qip.system, "query_windows", return_value="WINDOWS_SYSTEM_MAPPING"
    )


@pytest.mark.parametrize("platform, expected", [
    ("Linux", "LINUX_SYSTEM_MAPPING"),
    ("Darwin", "MAC_SYSTEM_MAPPING"),
    ("Windows", "WINDOWS_SYSTEM_MAPPING")
], ids=[
    "linux",
    "mac",
    "windows",
])
@pytest.mark.usefixtures("mocked_query_linux")
@pytest.mark.usefixtures("mocked_query_mac")
@pytest.mark.usefixtures("mocked_query_windows")
def test_query(mocked_platform_system, platform, expected):
    """Query system mapping."""
    mocked_platform_system.return_value = platform
    assert qip.system.query() == expected


def test_query_version_error(mocked_platform_system, mocked_platform_linux):
    """Fails to query system mapping from incorrect os version."""
    mocked_platform_system.return_value = "linux"
    mocked_platform_linux.side_effect = InvalidVersion

    with pytest.raises(RuntimeError):
        qip.system.query()


@pytest.mark.parametrize("distribution, architecture, expected", [
    (
        ("centos", "7.3.1611", "Core"), "x86_64",
        {
            "platform": "linux",
            "arch": "x86_64",
            "os": {"name": "centos", "major_version": 7}
        }
    ),
    (
        ("centos", "6.5", "Final"), "x86_64",
        {
            "platform": "linux",
            "arch": "x86_64",
            "os": {"name": "centos", "major_version": 6}
        }
    ),
    (
        ("redhat", "5.7", "Final"), "i386",
        {
            "platform": "linux",
            "arch": "i386",
            "os": {"name": "redhat", "major_version": 5}
        }
    )
], ids=[
    "centos-7-64b",
    "centos-6-64b",
    "redhat-5-32b",
])
def test_query_linux(
    mocked_platform_linux, mocked_platform_machine,
    distribution, architecture, expected
):
    """Query linux system mapping."""
    mocked_platform_linux.return_value = distribution
    mocked_platform_machine.return_value = architecture
    assert qip.system.query_linux() == expected


@pytest.mark.parametrize("mac_ver, architecture, expected", [
    (
        ("10.13.3", ("", "", ""), ""), "x86_64",
        {
            "platform": "mac",
            "arch": "x86_64",
            "os": {"name": "mac", "major_version": 10}
        }
    ),
    (
        ("9.0.0", ("", "", ""), ""), "x86_64",
        {
            "platform": "mac",
            "arch": "x86_64",
            "os": {"name": "mac", "major_version": 9}
        }
    )
], ids=[
    "mac-10.13",
    "mac-9.0",
])
def test_query_mac(
    mocked_platform_mac, mocked_platform_machine,
    mac_ver, architecture, expected
):
    """Query mac system mapping."""
    mocked_platform_mac.return_value = mac_ver
    mocked_platform_machine.return_value = architecture
    assert qip.system.query_mac() == expected


@pytest.mark.parametrize("win32_ver, architecture, expected", [
    (
        ("XP", "5.1.2600", "SP2", "Multiprocessor Free"), "i386",
        {
            "platform": "windows",
            "arch": "i386",
            "os": {"name": "windows", "major_version": 5}
        }
    ),
    (
        ("10", "10.0.16299", "", "Multiprocessor Free"), "AMD64",
        {
            "platform": "windows",
            "arch": "AMD64",
            "os": {"name": "windows", "major_version": 10}
        }
    )
], ids=[
    "windows-xp",
    "windows-10",
])
def test_query_windows(
    mocked_platform_win32, mocked_platform_machine,
    win32_ver, architecture, expected
):
    """Query mac system mapping."""
    mocked_platform_win32.return_value = win32_ver
    mocked_platform_machine.return_value = architecture
    assert qip.system.query_windows() == expected


def test_extract_major_version():
    """Extract major version of operating system request for *version*."""
    major_version = qip.system._extract_major_version("10.5.0")
    assert major_version == 10
