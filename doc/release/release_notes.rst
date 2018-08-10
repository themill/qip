.. _release/release_notes:

*************
Release Notes
*************

.. release:: 0.2.0

    .. change:: changed

        Remove support for depfile

    .. change:: changed

        Use rsync to move temp folder to install location

    .. change:: changed

        PEP8 code style cleanup

    .. change:: new
        :tags: documentation

        Add auto API docs and doc strings

    .. change:: changed

        Remove unused arguments and variables

    .. change:: changed

        password and target options are now in the commandline list but if not set the
        user will be prompted to enter them as before. This should facilitate testing

    .. change:: changed

        Functions in qipcore no longer sys.exit but raise QipError instead

    .. change:: changed

        Print statements are replaced with mlog info statements with the user
        tag set to True so they always show regardless of verbosity

    .. change:: changed

        Remove depfile functionality as it was only for testing

    ..change:: new

        Add unit tests

    ..change:: new

        Sync installs to all sites automatically

    ..change:: changed

        Move config settings to click context

    ..change:: new

        QipCore now raises expceptions instead of exiting

.. release:: 0.1.0

    .. change:: new

        Initial release.
