nomad destroy
=============

**Command:** ``nomad destroy [name [name ...]]``

This command can be used to destroy containers. If the containers to be destroyed are still running
they will first be stopped.

By default this command will try to destroy all the containers of the current project but you can
limit this operation to some specific containers by specifying their names. Keep in mind that a
confirmation will be prompted to the user when using the `destroy` command.

Options
-------

* ``[name [name ...]]`` - zero, one or more container names
* ``--force`` or ``-f`` - this option allows to destroy containers without confirmation

Examples
--------

.. code-block:: console

  $ nomad destroy               # destroys all the containers of the project
  $ nomad destroy mycontainer   # destroys the "mycontainer" container
  $ nomad destroy web ci        # destroys the "web" and "ci" containers
  $ nomad destroy --force web   # destroys the "web" container without confirmation
