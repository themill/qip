.. _release/release_notes:

*************
Release Notes
*************

.. release:: Upcoming

    .. change:: new

        Write out requirement files into package directories, detailing
        what requirements that package has. The file will be in the
        same directory as the install and be called `requirements.json`

        The format will be

        .. code:: json

            [
                {
                    "MarkupSafe": "/tmp/installs/MarkupSafe/MarkupSafe-1.0"
                }
            ]

    .. change:: new

        Rewrite of qip functionality. Only installs packages locally.


.. release:: 0.1.0

    .. change:: new

        Initial release.
