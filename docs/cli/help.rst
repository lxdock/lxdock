nomad help
==========

**Command:** ``nomad help [subcommand]``

This command can be used to show help information.

By default this command will show the global help information for the ``nomad`` cli but you can also
get help information for a specific subcommand.

Options
-------

* ``[subcommand]`` - a subcommand name (eg. ``up``, ``halt``, ...)

Examples
--------

.. code-block:: console

  $ nomad help               # shows the global help information
  $ nomad help destroy       # shows help information for the "destroy" subcommand
