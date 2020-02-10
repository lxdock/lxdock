#####
Shell
#####

The shell provisioner allows you to execute commands on the guest side or the host side in order to
provision your containers.

Usage
-----

Just append a ``shell`` provisioning operation to your LXDock file as follows:

.. code-block:: yaml

  name: myproject
  image: ubuntu/bionic

  provisioning:
    - type: shell
      inline: cd /tmp && echo "Here's the PATH" $$PATH >> test.txt

.. note::

  The inline command is executed by ``sh -c 'command_line'``. Keep in mind that dollar sign ``$``
  means string interpolation in YAML and it is necessary to put ``$$`` to escape the dollar sign.

Required options
----------------

inline
======

The ``inline`` option allows you to specify a shell command that should be executed on the guest
side or on the host. Note that the ``inline`` option and the ``script`` option are mutually
exclusive.

.. code-block:: yaml

  [...]
  provisioning:
    - type: shell
      inline: echo "Hello, World!"

script
======

The ``script`` option lets you define the path to an existing script that should be executed on the
guest side or on the host. Note that the ``script`` option and the ``inline`` option are mutually
exclusive.

.. code-block:: yaml

  [...]
  provisioning:
    - type: shell
      script: path/to/my/script.sh

Optional options
----------------

side
====

Use the ``side`` option if you want to define that the shell commands/scripts should be executed on
the host side. The default value for this option is ``guest``. Here is an example:

.. code-block:: yaml

  [...]
  provisioning:
    - type: shell
      side: host
      inline: echo "Hello, World!"
