# :coding: utf-8

import os

import pytest

import qip.filesystem


def test_ensure_directory(temporary_directory, temporary_file):
    """Create directory if it doesn't exist."""
    path1 = os.path.join(temporary_directory, "path1")
    path2 = os.path.join(path1, "path2")
    assert os.path.isdir(path1) is False
    assert os.path.isdir(path2) is False

    qip.filesystem.ensure_directory(path2)
    assert os.path.isdir(path1) is True
    assert os.path.isdir(path2) is True

    # Do not raise when folder exists
    qip.filesystem.ensure_directory(path2)

    # Raise when element is a file
    with pytest.raises(OSError):
        qip.filesystem.ensure_directory(temporary_file)

    # Raise for other errors
    with pytest.raises(OSError):
        qip.filesystem.ensure_directory("/incorrect")


def test_remove_directory_content(temporary_directory):
    """Remove content of a directory."""
    _file = open(os.path.join(temporary_directory, "test"), 'w')
    _file.close()
    assert len(os.listdir(temporary_directory)) == 1

    qip.filesystem.remove_directory_content(temporary_directory)

    assert os.path.isdir(temporary_directory) is True
    assert len(os.listdir(temporary_directory)) == 0


def test_remove_directory_content_fail(temporary_directory):
    """Fail to remove content of a file."""
    _path = os.path.join(temporary_directory, "test")
    _file = open(_path, 'w')
    _file.close()
    assert len(os.listdir(temporary_directory)) == 1

    with pytest.raises(OSError):
        qip.filesystem.remove_directory_content(_path)


def test_sanitise_value():
    """Sanitize value."""
    value = "/path/to/a-file/with: A F@#%ing Name!!!"
    assert qip.filesystem.sanitize_value(value) == (
        "/path/to/a-file/with:_A_F__%ing_Name___"
    )

    assert qip.filesystem.sanitize_value(value, substitution_character="-") == (
        "/path/to/a-file/with:-A-F--%ing-Name---"
    )

    assert qip.filesystem.sanitize_value(value, case_sensitive=False) == (
        "/path/to/a-file/with:_a_f__%ing_name___"
    )
