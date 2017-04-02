############
Provisioners
############

LXDock provides support for common provisioning operations. Provisioning operations can be easily
defined in your LXDock file using the ``provisioning`` option:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  provisioning:
    - type: ansible
      playbook: deploy/site.yml

.. warning::

  When using provisioners you should keep in mind that some of them can execute local actions on the
  host. For example Ansible playbooks can trigger local actions that will be run on your system.
  Other provisioners (like the shell provisioner) can define commands to be runned on the host side
  or in provileged containers. **You have to** trust the projects that use these provisioning tools
  before running LXDock!

Documentation sections for the supported provisioning tools or methods are listed here.

.. toctree::
    :maxdepth: 1

    ansible
    shell
