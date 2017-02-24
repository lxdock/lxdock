lxdock provision
================

**Command:** ``lxdock provision [name [name ...]]``

This command can be used to provision your containers.

By default it will install bare bones packages (openssh, python) into your container if the
underlying distribution is supported by LXDock. That said, the ``provision`` command can also
trigger the execution of provisioning tools that you could've configured in your LXDock file (using
the ``provisioning`` block).

Options
-------

* ``[name [name ...]]`` - zero, one or more container names

Examples
--------

.. code-block:: console

  $ lxdock provision               # provisions all the containers of the project
  $ lxdock provision mycontainer   # provisions the "mycontainer" container
  $ lxdock provision web ci        # provisions the "web" and "ci" containers
