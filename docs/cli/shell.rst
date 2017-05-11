lxdock shell
============

**Command:** ``lxdock shell [name] [arguments]``

This command can be used to open an interactive shell inside one of your containers.
If ``-c`` is specified, execute the command line instead of opening the shell.

By default, that shell logins as ``root`` unless your LXDock config specifies another user
in its ``shell`` option. In all cases, the ``--user`` command line overrides everything.

Options
-------

* ``[name]`` - a container name
* ``-u, --user <username>`` - user to login as
* ``-c, --command <command_line>`` - command to be executed in the shell

Examples
--------

.. code-block:: console

  $ lxdock shell mycontainer       # opens a shell into the "mycontainer" container
  $ lxdock shell -u root           # opens a shell as root, regardless of our config
  $ lxdock shell mycontainer -c echo HELLO      # executes "echo HELLO" in "mycontainer"
  $ lxdock shell mycontainer -c echo '$PATH'    # executes "echo '$PATH'" in "mycontainer"


For the last example, you will see "$PATH" as-is. It is not evaluated as a variable.
