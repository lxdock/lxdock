Getting started
===============

Requirements
------------

* `Python`_ 3.4+
* `LXD`_ 2.0+
* ``getfacl/setfacl`` if you plan to use shared folders
* any provisioning tool you wish to use with LXDock

.. _Python: https://www.python.org
.. _LXD: https://www.ubuntu.com/cloud/lxd

Building LXDock on Linux
------------------------

LXDock should build very easily on Linux provided you have LXD available on your system.

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
    $ lxc network create lxdbr0 ipv6.address=none ipv4.address=10.0.3.1/24 ipv4.nat=true
    $ lxc network attach-profile lxdbr0 default eth0

You can now check if your LXD installation is working using:

  .. code-block:: console

    $ lxc launch ubuntu: first-machine && lxc exec first-machine bash

.. note::

  You can use ``lxc stop first-machine`` to stop the previously created container.

Install LXDock
~~~~~~~~~~~~~~

You should now be able to install LXDock using:

.. code-block:: console

  $ pip3 install git+git://github.com/lxdock/lxdock.git

.. note::

  Don't have ``pip3`` installed on your system? Most distros have a specific package for it, it's
  only a matter of installing it. For example, on Debian and Ubuntu, it's ``python3-pip``.
  Otherwise, `Stackoverflow can help you <http://stackoverflow.com/a/6587528>`__.

Command line completion
-----------------------

LXDock can provide completion for commands and container names.

Bash
~~~~

If you use Bash, you have to make sure that bash completion is installed (which should be the case
for most Linux installations). In order to get completion for LXDock, you should place the
``contrib/completion/bash/lxdock`` file at ``/etc/bash.completion.d/lxdock`` (or at any other place
where your distribution keeps completion files):

.. code-block:: console

  $ sudo cp contrib/completion/bash/lxdock /etc/bash.completion.d/lxdock

Make sure to restart your shell before trying to use LXDock's bash completion.

ZSH
~~~

*Not yet!* But feel free to contribute (please refer to :doc:`contributing`)!

Your first LXDock file
----------------------

Create a file called ``.lxdock.yml`` (or ``lxdock.yml``) in your project directory and paste the
following:

.. code-block:: yaml

  name: myproject

  containers:
    - name: test01
      image: ubuntu/xenial

    - name: test02
      image: archlinux

This LXDock file defines a project (``myproject``) and two containers, ``test01`` and ``test02``.
These containers will be constructed using respectively the ``ubuntu/xenial`` and the ``archlinux``
images (which will be pulled from an image server - https://images.linuxcontainers.org by default).

Now from your project directory, start up your containers using the following command:

.. code-block:: console

  $ lxdock up
  Bringing container "test01" up
  Bringing container "test02" up
  ==> test01: Unable to find container "test01" for directory "[PATH_TO_YOUR_PROJECT]"
  ==> test01: Creating new container "myproject-test01-11943450" from image ubuntu/xenial
  ==> test01: Starting container "test01"...
  ==> test01: No IP yet, waiting 10 seconds...
  ==> test01: Container "test01" is up! IP: [CONTAINER_IP]
  ==> test01: Doing bare bone setup on the machine...
  ==> test01: Adding ssh-rsa [SSH_KEY] to machine's authorized keys
  ==> test01: Provisioning container "test01"...
  ==> test02: Unable to find container "test02" for directory "[PATH_TO_YOUR_PROJECT]"
  ==> test02: Creating new container "myproject-test02-11943450" from image archlinux
  ==> test02: Starting container "test02"...
  ==> test02: No IP yet, waiting 10 seconds...
  ==> test02: Container "test02" is up! IP: [CONTAINER_IP]
  ==> test02: Doing bare bone setup on the machine...
  ==> test02: Adding ssh-rsa [SSH_KEY] to machine's authorized keys
  ==> test02: Provisioning container "test02"...

*Congrats! You're in!*

Problems?
---------

If you're having problems trying to run your container, try running them in :ref:`conf-privileged`
mode. Many older distributions have an init system that doesn't work well with unprivileged
containers (`debian/jessie` notably). Some host-side problems can also be worked around by running
privileged containers.
