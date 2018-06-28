.. _tutorial:

********
Tutorial
********

Downloading a package
---------------------

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

A downloaded package is easily installed with

.. code-block:: bash

    $> qip install shadow==3.4.0

This will start resolving dependencies and offer to download and install these too. If you
want to automatically download dependencies, without any interaction, use the --download options

.. code-block:: bash

    $> qip install shadow==3.4.0 --download

If on the other hand you want to only install the specified package, use the --nodeps flag

.. code-block:: bash

    $> qip install shadow==3.4.0 --nodeps

You will notice that you are prompted to enter a target. Currently these are ``Centos72``,
``Centos65``, adn ``localhost``. Localhost is used for CI deployment only as it will
run the qip commands on the local machine as admin3d, and most machines are not setup
with passwordless admin3d sudo.

If you select one of the other machines, you will be prompted to enter your user password
before the installation/download will begin.