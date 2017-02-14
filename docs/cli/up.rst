nomad up
========

**Command:** ``nomad up [name [name ...]]``

This command can be used to start the containers of your project.

By default this command will try to start all the containers of your project but you can limit this
operation to some specific containers by specifying their names. It should be noted that containers
will be created (and provisioned) if they don't exist yet.

Options
-------

* ``[name [name ...]]`` - zero, one or more container names

Examples
--------

.. code-block:: console

  $ nomad up               # starts the containers of the project
  $ nomad up mycontainer   # starts the "mycontainer" container
  $ nomad up web ci        # starts the "web" and "ci" containers
