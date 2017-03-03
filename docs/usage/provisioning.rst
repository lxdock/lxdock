############
Provisioning
############

LXDock supports many provisioning tools in order to allow you to easily provision containers created
using LXD. Using provisioning tools such as Ansible with LXDock will allow you to alter the
configuration, install software, deploy applications and more on the containers. Using the built-in
provisioning capabilities of LXDock will allow you to run these provisioning operations as part of
the ``lxdock up`` wokflow. To be more precise, the provisioning tools associated with your LXDock
configuration are executed in the following situations:

* when you run ``lxdock up`` the first time; that is when the container does not exist yet
* when you run ``lxdock provision``. Note that you can run this command as many time as you want

Currently, LXDock provides a built-in support for the following provisioning tools:

* Ansible
* *Your favorite provisioning tool is not listed here?!!* Feel free to contribute!

The provisioning tools you choose to use can be configured in your LXDock file using the
``provisioning`` option. For example, we could choose to provision our containers using an Ansible
playbook as follows:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  provisioning:
    - type: ansible
      playbook: deploy/site.yml

Note that you can use *many* provisioning tools. The order in which provisioning tools are defined
in your LXdock file defines the order in which they are executed.
