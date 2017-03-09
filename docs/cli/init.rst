lxdock init
===========

**Command:** ``lxdock init``

This command can be used to generate a LXDock file containing highlights regarding some useful
options.

Options
-------

* ``--image`` - this option allows to use a specific container image in the generated configuration
* ``--project`` - this option allows to define the name of the project that will appear in the LXDock file
* ``--force`` or ``-f`` - this option allows to overwrite an exsting LXDock file if any

Examples
--------

.. code-block:: console

  $ lxdock init                          # generates a basic LXDock file
  $ lxdock init --image debian/jessie    # generates a LXDock file defining a debian/jessie container
  $ lxdock init --project myproject      # generates a basic LXDock file defining a "myproject" project
  $ lxdock init --force                  # overwrite an existing LXDock file if applicable
