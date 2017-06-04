lxdock up
=========

**Command:** ``lxdock up [name [name ...]] [arguments]``

This command can be used to start the containers of your project.

By default this command will try to start all the containers of your project but you can limit this
operation to some specific containers by specifying their names. It should be noted that containers
will be created (and provisioned) if they don't exist yet.

Options
-------

* ``[name [name ...]]`` - zero, one or more container names
* ``--provision`` - this option allows to force containers to be provisioned
* ``--no-provision`` - this option allows to disable container provisioning

Examples
--------

.. code-block:: console

  $ lxdock up                 # starts the containers of the project
  $ lxdock up mycontainer     # starts the "mycontainer" container
  $ lxdock up web ci          # starts the "web" and "ci" containers
  $ lxdock up --provision     # starts the containers of the project and provision them (even if they were already created)
  $ lxdock up --no-provision  # starts the containers of the project but disable the provisioning step
