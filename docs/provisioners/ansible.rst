#######
Ansible
#######

LXDock provides built-in support for `Ansible`_ provisioning.

.. _Ansible: https://www.ansible.com/

Requirements
------------

`Ansible`_ v2.0+

Usage
-----

Just append an ``ansible`` provisioning operation to your LXDock file as follows:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  provisioning:
    - type: ansible
      playbook: deploy/site.yml

Required options
----------------

playbook
========

The ``playbook`` option allows you to define the path to your Ansible playbook you want to run when
your containers are provisioned.

Optional options
----------------

ask_vault_pass
==============

You can use this option to force the use of the ``--ask-vault-pass`` flag when the
``ansible-playbook`` command is executed during the provisioning workflow. Here is an example:

.. code-block:: yaml

  [...]
  provisioning:
    - type: ansible
      playbook: deploy/site.yml
      ask_vault_pass: yes

vault_password_file
===================

You can use this option to specify the path toward the vault password file you want to use when the
``ansible-playbook`` command is executed. Here is an example:

.. code-block:: yaml

  [...]
  provisioning:
    - type: ansible
      playbook: deploy/site.yml
      vault_password_file: secrets/vaultpass

.. _Ansible: https://www.ansible.com/
