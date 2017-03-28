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

Documentation sections for the supported provisioning tools or methods are listed here.

.. toctree::
    :maxdepth: 1

    ansible
