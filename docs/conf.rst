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
  mode: pull
  image: ubuntu/xenial

  containers:
    - name: test01
    - name: test02
    - name: test03
      image: debian/jessie

This section contains a list of all configuration options supported by Nomad files.

hostnames
---------

The ``hostnames`` option allows you to define which hostnames should be configured for your
containers. These hostnames will be added to your ``/etc/hosts`` file, thus allowing you to easily
access your applications or services.

.. code-block:: yaml

  name: myproject
  mode: pull
  image: ubuntu/xenial

  containers:
    - name: test01
      hostnames:
        - myapp.local
        - myapp.test
    - name: test02
