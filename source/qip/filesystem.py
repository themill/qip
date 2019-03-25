# :coding: utf-8

import os
import errno
import unicodedata
import re
import shutil


def ensure_directory(path):
    """Ensure directory exists at *path*.

    :param path: Path to create if necessary.

    :return: None.

    """
    # Explicitly indicate that path should be a directory as default OSError
    # raised by 'os.makedirs' just indicates that the file exists, which is a
    # bit confusing for user.
    if os.path.isfile(path):
        raise OSError("'{}' should be a directory".format(path))

    try:
        os.makedirs(path)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

        if not os.path.exists(path):
            raise


def remove_directory_content(path):
    """Remove content of *path* directory.

    :param path: Path from which all content should be removed.

    :return: None.

    """
    if not os.path.isdir(path):
        raise OSError("'{}' should be a directory".format(path))

    shutil.rmtree(path)
    ensure_directory(path)


def sanitize_value(value, substitution_character="_", case_sensitive=True):
    """Return *value* suitable for use with filesystem.

    Replace awkward characters with *substitution_character*. Where possible,
    convert unicode characters to their closest "normal" form.

    If not *case_sensitive*, then also lowercase value.

    :param value: String value to sanitise.
    :param substitution_character: Substitution for incorrect value.
    :param case_sensitive: indicate whether case should be preserved. Otherwise
        the returned value will be lower case. Default is True.

    :return: Sanitized value.

    """
    if isinstance(value, str):
        value = value.decode("utf-8")

    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore")
    value = re.sub(r"[^\w._\-\\/:%]", substitution_character, value)
    value = value.strip()

    if not case_sensitive:
        value = value.lower()

    return unicode(value)
