.. _tutorial:

********
Tutorial
********

Downloading a package
---------------------

.. Note::

    This will become obsolete when devpi server integration is complete in qip

To download a package use the download command

.. code-block:: bash

    $> qip download flask

This command takes no options. In this case it will locate the latest version of flask and
download it to the configured package index. If you want a specific version specify it as
per Python standards, for example

.. code-block:: bash

   $> qip download flask==1.2.0

If you want to download something for the Gitlab repo, use the repos SSH URL

.. code-block:: bash

    $> qip download git@gitlab:production-technology/shadow.git@3.4.0


Installing a package
--------------------

To install a package use the `install` command. If you omit the target
or password options, then you will be prompted to select a known
target from a list, as well as a prompt fro the password.

For example:

.. code-block:: Python

    $> qip install flask
       Targets:
       [0]  centos65
       [1]  centos72
       [2]  localhost

       Select a target [0]:

Once the target is selected you will be asked for a password, except for the case
of the localhost.

qip will then proceed to resolve dependencies and install the packages as required.

If you want to install a single package without any of its dependencies, you
can pass the `--no-deps` argument to the install command

.. code-block:: bash

    $> qip install --nodeps flask

If you are installing a package that already exists, then you will asked if you
want to overwrite it. You can skip these prompts and assume "yes" with the `-y`
option.