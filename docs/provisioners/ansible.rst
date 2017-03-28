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

*Not yet!*

.. _Ansible: https://www.ansible.com/
