nomad provision
===============

**Command:** ``nomad provision [name [name ...]]``

This command can be used to provision your containers.

By default it will install bare bones packages (openssh, python) into your container if the
underlying distribution is supported by LXD-Nomad. That said, the ``provision`` command can also
trigger the execution of provisioning tools that you could've configured in your Nomad file (using
the ``provisioning`` block).

Options
-------

* ``[name [name ...]]`` - zero, one or more container names

Examples
--------

.. code-block:: console

  $ nomad provision               # provisions all the containers of the project
  $ nomad provision mycontainer   # provisions the "mycontainer" container
  $ nomad provision web ci        # provisions the "web" and "ci" containers
