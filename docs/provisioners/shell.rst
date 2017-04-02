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
  image: ubuntu/xenial

  provisioning:
    - type: shell
      inline: echo "Hello, World!"

.. note::

  Keep in mind that the shell provisioner will use the LXD's ``exec`` method in order to run your
  commands on containers (the same method used by the ``lxc exec`` command). This means that common
  shell patterns (like file redirects, ``|``, ``>``, ``<``, ...) won't work because the ``exec``
  method doesn't use a shell (so the kernel will not be able to understand these shell patterns).
  The only way to overcome this is to put things like ``sh -c 'ls -l > /tmp/test'`` in your
  ``inline`` options.

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
