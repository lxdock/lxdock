Command-line reference
======================

Most of your interaction with LXDock will be done using the ``lxdock`` command.
This command provides many subcommands:
``up``, ``halt``, ``destroy``, etc.

.. code-block:: console

  $ lxdock --help
  usage: lxdock [-h] [--version] [-v]
              {config,destroy,halt,help,init,provision,shell,status,up} ...

  Orchestrate and run multiple containers using LXD.

  positional arguments:
    {config,destroy,halt,help,init,provision,shell,status,up}
      config              Validate and show the LXDock file.
      destroy             Stop and remove containers.
      halt                Stop containers.
      help                Show help information.
      init                Generate a LXDock file.
      provision           Provision containers.
      shell               Open a shell or execute a command in a container.
      status              Show containers' statuses.
      up                  Create, start and provision containers.

  optional arguments:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    -v, --verbose

The subcommands are described in the
following pages but you can easily get help using the ``help`` subcommand. ``lxdock help`` will
display help information for the ``lxdock`` command while ``lxdock help [subcommand]`` will show the
help for a specific subcommand. For example:

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
  init
  provision
  shell
  status
  up
