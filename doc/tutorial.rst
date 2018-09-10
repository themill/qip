.. _tutorial:

********
Tutorial
********

Installing a package
--------------------

To install a package use the `install` command. If you omit the target
or password options, then you will be prompted to select a known
target from a list, as well as a prompt fro the password.

For example:

.. code-block:: bash

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