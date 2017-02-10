Getting started
===============

Requirements
------------

* `Python`_ 3.4+
* `LXD`_ 2.0+
* ``getfacl/setfacl`` if you plan to use shared folders
* any provisioning tool you wish to use with LXD-Nomad

.. _Python: https://www.python.org
.. _LXD: https://www.ubuntu.com/cloud/lxd

Building nomad on Linux
-----------------------

LXD-Nomad should build very easily on Linux provided you have LXD available on your system.

Prerequisite: install LXD
~~~~~~~~~~~~~~~~~~~~~~~~~

You may want to skip this section if you already have a working installation of LXD on your system.

For Debian and Ubuntu, the following command will ensure that LXD is installed:

.. code-block:: console

  $ sudo apt-get install lxd

.. note::

  If you're using an old version of Ubuntu you should first add the LXD's apt repository and install
  the ``lxd`` package as follows:

  .. code-block:: console

    $ sudo add-apt-repository -y ppa:ubuntu-lxc/lxd-stable
    $ sudo apt-get update
    $ sudo apt-get install lxd

You should now be able to configure your LXD installation using:

.. code-block:: console

  $ newgrp lxd  # ensure your current user can use LXD
  $ sudo lxd init

.. note::

  The ``lxd init`` command will ask you to choose the settings to apply to your LXD installation in
  an interactive way (storage backend, network configuration, etc). But if you just want to go fast
  you can try the following commands:

  .. code-block:: console

    $ newgrp lxd
    $ sudo lxd init --auto
    $ sudo lxc network create lxdbr0 ipv6.address=none ipv4.address=10.0.3.1/24 ipv4.nat=true
    $ sudo lxc network attach-profile lxdbr0 default eth0

You can now check if your LXD installation is working using:

  .. code-block:: console

    $ lxc launch ubuntu: first-machine && lxc exec first-machine bash

.. note::

  You can use ``lxd stop first-machine`` to stop the previously created container.

Install LXD-Nomad
~~~~~~~~~~~~~~~~~

Yoi should now be able to install LXD-Nomad using:

.. code-block:: console

  $ pip3 install git+git://github.com/lxd-nomad/lxd-nomad.git
