Nomad file reference
====================

Nomad files allow you to defines which containers should be created for your projects. Nomad files
are YML_ files and should define basic information allowing LXD-Nomad to properly create your
containers (eg. container names, images, ...). By default LXD-Nomad will try to use a file located
at ``./.nomad.yml``.

.. _YML: http://yaml.org/

.. note::

  LXD-Nomad supports the following names for Nomad files: ``.nomad.yml``, ``nomad.yml``,
  ``.nomad.yaml`` and ``nomad.yaml``.

A container definition contains parameters that will be used when creating each container of a
specific project. It should be noted that most of the options that you can define in your Nomad file
can be applied "globally" or in the context of a specific container. For example you can define a
global ``image`` option telling to use the ``ubuntu/xenial`` for all your containers and decide to
use the ``debian/jessie`` image for a specific container:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  containers:
    - name: test01
    - name: test02
    - name: test03
      image: debian/jessie

This section contains a list of all configuration options supported by Nomad files.

containers
----------

The ``containers`` block allows you to define the containers of your project. It should be a list of
containers, as follows:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  containers:
    - name: test01
    - name: test02

hostnames
---------

The ``hostnames`` option allows you to define which hostnames should be configured for your
containers. These hostnames will be added to your ``/etc/hosts`` file, thus allowing you to easily
access your applications or services.

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  containers:
    - name: test01
      hostnames:
        - myapp.local
        - myapp.test
    - name: test02

image
-----

The ``image`` option should contain the alias of the image you want to use to build your containers.
LXD-Nomad will try to pull images from the default LXD's image server. So you can get a list of
supported aliases by visiting https://images.linuxcontainers.org/ or by listing the aliases of the
"images:" default remote:

.. code-block:: console

  $ lxc image alias list images:

There are many scenarios to consider when you have to choose the value of the ``image`` option. If
you choose to set your ``image`` option to ``ubuntu/xenial`` this means that the container will use
the Ubuntu's Xenial version with the same architecture as your host machine (amd64 in most cases).
It should be noted that the ``image`` value can also contain a container alias that includes the
targetted architecture (eg. ``debian/jessie/amd64`` or ``ubuntu/xenial/armhf``).

Here is an example:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

You should note that you can also use "local" container aliases. This is not the most common
scenario but you can manage your own image aliases and decide to use them with LXD-Nomad. You'll
need to use the ``mode: local`` option if you decide to do this (the default ``mode`` is ``pull``).
For example you could create an image associated with the ``old-ubuntu`` alias using:

.. code-block:: console

  $ lxc image copy ubuntu:12.04 local: --alias old-ubuntu

And then use it in your Nomad file as follows:

.. code-block:: yaml

  name: myproject
  image: old-ubuntu
  mode: local

mode
----

The ``mode`` option allows you to specify which mode to use in order to retrieve the images that
will be used to build your containers. Two values are allowed here: ``pull`` (which is the default
mode for LXD-Nomad) and ``local``. In ``pull`` mode container images will be pulled from an image
server (https://images.linuxcontainers.org/ by default). The ``local`` mode allows you to use local
container images (it can be useful if you decide to manage your own image aliases and want to use
them with LXD-Nomad).

privileged
----------

You should use the ``privileged`` option if you want to created privileged containers. Containers
created by LXD-Nomad are unprivileged by default. Such containers are safe by design because the
root user in the containers doesn't map to the host's root user: it maps to an unprivileged user
*outside* the container.

Here is an example on how to set up a privileged container in your Nomad file:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  containers:
    - name: web
      privileged: yes

.. note::

  Please refer to :doc:`glossary`  for more details on these notions.
