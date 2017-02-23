nomad shell
===========

**Command:** ``nomad shell [arguments] [name]``

This command can be used to open an interactive shell inside one of your containers.

By default, that shell logins as ``root`` unless your nomad config specifies another user
in its ``shell:`` option. In all cases, the ``--user`` command line overrides everything.

Options
-------

* ``[name]`` - a container name
* ``-u, --user <username>`` - user to login as

Examples
--------

.. code-block:: console

  $ nomad shell mycontainer       # opens a shell into the "mycontainer" container
  $ nomad shell -u root           # opens a shell as root, regardless of our config
