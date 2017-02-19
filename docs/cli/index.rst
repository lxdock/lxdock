Command-line reference
======================

Most of your interaction with Nomad will be done using the ``nomad`` command. This command provides
many subcommands: ``up``, ``halt``, ``destroy``, etc. These subcommands are described in the
following pages but you can easily get help using the ``help`` subcommand. ``nomad help`` will
display help information for the ``nomad`` command while ``nomad help [subcommand]`` will show the
help for a specifc subcommand. For example:

.. code-block:: console

  $ nomad help up
  usage: LXD-Nomad up [-h] [name [name ...]]

  Create, start and provision all the containers of the project according to
  your nomad file. If container names are specified, only the related containers
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
