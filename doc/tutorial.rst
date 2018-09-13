.. _tutorial:

********
Tutorial
********

Installing a package
--------------------

To install a package simply issue the `qip` command and specify
an output directory with `-o` or `--outdir`

For example:

.. code-block:: bash

    $> qip -o /tmp/my_installs flask

qip will then proceed to resolve dependencies and install the packages as required.

If you want to install a single package without any of its dependencies, you
can pass the `--nodeps` argument to the install command

.. code-block:: bash

    $> qip -o /tmp/my_installs --nodeps flask

If you are installing a package that already exists, then you will asked if you
want to overwrite it. You can skip these prompts and assume "yes" with the `-y`
option.