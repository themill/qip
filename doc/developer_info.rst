.. _developer_info:

**************
Developer Info
**************

When running on local host it will only work on hosts that you can
``sudo -u admin3d <cmd> on without a password`` - i.e. dev3d-2 and dev3d-3 at the moment.
To enable this run the following as root on the target machine:

.. code-block:: bash

	sh -c 'echo "ALL ALL=(admin3d:admin3d) NOPASSWD:ALL" > /etc/sudoers.d/admin3d'

If you are running the commands remote (over paramiko) then the remote machine must
have passwordless sudo to the admin3d user enabled as well as sudo configured to
disabled ``Defaults requiretty``. You can edit the ``/etc/sudoers`` file to remove
this option.
If the machine requires a tty for sudo then the output from the paramiko commands
will get merged into stdout and stderr, which breaks qip's ability to parse output
from these commands (pip mostly).

Running on localhost will not require the tty to be disabled. So if running via CI, the target setting should be localhost, passed in via the commandline option (else there will be a prompt). The localhost target will detect and modify the install and package dirs to the match the platform of the host (el7, el6). This of course will require each CI task to have a specified runner, to make sure they land on the correct platforms.