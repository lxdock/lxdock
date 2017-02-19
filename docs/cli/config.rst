nomad config
============

**Command:** ``nomad config``

This command can be used to validate and print the Nomad config file of the project.

Options
-------

* ``--containers`` - prints only container names, one per line

Examples
--------

.. code-block:: console

  $ nomad config                 # prints project's Nomad file
  $ nomad config --containers    # prints project's container names
