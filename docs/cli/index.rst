Command-line reference
======================

Most of your interaction with LXDock will be done using the ``lxdock`` command. This command provides
many subcommands: ``up``, ``halt``, ``destroy``, etc. These subcommands are described in the
following pages but you can easily get help using the ``help`` subcommand. ``lxdock help`` will
display help information for the ``lxdock`` command while ``lxdock help [subcommand]`` will show the
help for a specifc subcommand. For example:

.. code-block:: console

  $ lxdock help up
  usage: lxdock up [-h] [name [name ...]]

  Create, start and provision all the containers of the project according to
  your LXDock file. If container names are specified, only the related containers
  are created, started and provisioned.

  positional arguments:
    name        Container name.

  optional arguments:
    -h, --help  show this help message and exit

.. toctree::
  :maxdepth: 1

  config
  destroy
  halt
  help
  provision
  shell
  status
  up
