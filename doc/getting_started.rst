.. _getting_started:

***************
Getting started
***************

.. highlight:: shell

Once :ref:`installed <installing>`, the command line tool can be used in a shell
as follows::

    >>> qip -h

To install a package available on :term:`PyPi` with its dependencies, simply run
the following command::

    >>> qip install ipython

.. note::

    Packages deployed in a custom index such as :term:`Devpi` will also be
    available.

By default, the Python packages and corresponding :term:`Wiz` definition will be
installed in the temporary path of the station::

    >>> tree -L 3 /tmp/qip
    ├── definitions
    │   ├── library-appnope-0.1.0-wfOwykDoXMk2LHJ6B1X0ZWpB-Js.json
    │   ├── library-backcall-0.2.0.json
    │   ├── library-decorator-4.4.2.json
    │   ├── library-ipython-7.18.1.json
    │   ├── library-ipython-genutils-0.2.0.json
    │   ├── library-jedi-0.17.2.json
    │   ├── library-parso-0.7.1.json
    │   ├── library-pexpect-4.8.0-wfOwykDoXMk2LHJ6B1X0ZWpB-Js.json
    │   ├── library-pickleshare-0.7.5.json
    │   ├── library-prompt-toolkit-3.0.7.json
    │   ├── library-ptyprocess-0.6.0-wfOwykDoXMk2LHJ6B1X0ZWpB-Js.json
    │   ├── library-pygments-2.7.0.json
    │   ├── library-setuptools-50.3.0.json
    │   ├── library-traitlets-5.0.4.json
    │   └── library-wcwidth-0.2.5-wfOwykDoXMk2LHJ6B1X0ZWpB-Js.json
    └── packages
        ├── Pygments
        │   └── Pygments-2.7.0-py38
        ├── appnope
        │   └── appnope-0.1.0-py38-mac10
        ├── backcall
        │   └── backcall-0.2.0-py38
        ├── decorator
        │   └── decorator-4.4.2-py38
        ├── ipython
        │   └── ipython-7.18.1-py38
        ├── ipython-genutils
        │   └── ipython-genutils-0.2.0-py38
        ├── jedi
        │   └── jedi-0.17.2-py38
        ├── parso
        │   └── parso-0.7.1-py38
        ├── pexpect
        │   └── pexpect-4.8.0-py38-mac10
        ├── pickleshare
        │   └── pickleshare-0.7.5-py38
        ├── prompt-toolkit
        │   └── prompt-toolkit-3.0.7-py38
        ├── ptyprocess
        │   └── ptyprocess-0.6.0-py38-mac10
        ├── setuptools
        │   └── setuptools-50.3.0-py38
        ├── traitlets
        │   └── traitlets-5.0.4-py38
        └── wcwidth
            └── wcwidth-0.2.5-py38-mac10

The :term:`Wiz` definition for "ipython" will look as follows:

.. code-block:: json

    {
        "identifier": "ipython",
        "version": "7.18.1",
        "namespace": "library",
        "description": "IPython: Productive Interactive Computing",
        "install-root": "/tmp/qip/packages",
        "command": {
            "iptest": "python -m IPython.testing.iptestcontroller",
            "iptest3": "python -m IPython.testing.iptestcontroller",
            "ipython": "python -m IPython",
            "ipython3": "python -m IPython"
        },
        "environ": {
            "PYTHONPATH": "${INSTALL_LOCATION}:${PYTHONPATH}"
        },
        "variants": [
            {
                "identifier": "3.8",
                "install-location": "${INSTALL_ROOT}/ipython/ipython-7.18.1-py38/lib/python3.8/site-packages",
                "requirements": [
                    "python >= 3.8, < 3.9",
                    "library::decorator[3.8]",
                    "library::traitlets[3.8] >=4.2",
                    "library::jedi[3.8] >=0.10",
                    "library::prompt-toolkit[3.8] >=2.0.0, <3.1.0, !=3.0.1, !=3.0.0",
                    "library::pexpect[3.8] >4.3",
                    "library::pygments[3.8]",
                    "library::appnope[3.8]",
                    "library::backcall[3.8]",
                    "library::setuptools[3.8] >=18.5",
                    "library::pickleshare[3.8]"
                ]
            }
        ]
    }

By default, Qip will install Python packages using the current
:data:`Python executable <sys.executable>`. It is possible to change it with
the :option:`-p/--python <qip install --python>` option::

    >>> qip install -u -p `which python2` ipython

.. note::

    The :option:`-u/--update <qip install --update>` option is used to
    update existing :term:`Wiz` definitions with new variants corresponding to
    the Python version used (e.g. "2.7").

If :term:`Wiz` definitions are already deployed for the Python interpreter,
it is possible to use a request instead of a Python executable path::

    >>> qip install -u -p "python==2.7.*" ipython

.. seealso::

    :ref:`Getting Started with Wiz <wiz:getting_started>`

Qip is a lightweight command line tool built over the :term:`Pip` command,
therefore it is possible to install packages as follows::

    >>> qip install .
    >>> qip install /path/to/foo/
    >>> qip install "foo==0.1.0"
    >>> qip install "foo >= 7, < 8"
    >>> qip install "git@github.com:foo/foo-api.git"
    >>> qip install "git@github.com:foo/foo-api.git@0.1.0"
    >>> qip install "git@github.com:foo/foo-api.git@dev"

As Python packages will not be installed in the same location, it is also
possible to install several versions of the same package::

    >>> qip install "ipython==7.*" "ipython==5.*"

If :term:`Wiz` definitions are already deployed for the dependent Python
interpreter, "ipython" can be run as follows::

    >>> wiz -add /tmp/qip/definitions run ipython

