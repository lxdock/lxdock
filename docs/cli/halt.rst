lxdock halt
===========

**Command:** ``lxdock halt [name [name ...]]``

This command can be used to halt running containers.

By default this command will try to halt all the containers of the current project but you can limit
this operation to some specific containers by specifying their names.

Options
-------

* ``[name [name ...]]`` - zero, one or more container names

Examples
--------

.. code-block:: console

  $ lxdock halt               # halts all the containers of the project
  $ lxdock halt mycontainer   # halts the "mycontainer" container
  $ lxdock halt web ci        # halts the "web" and "ci" containers
