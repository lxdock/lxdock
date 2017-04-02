LXDock file reference
=====================

LXDock files allow you to defines which containers should be created for your projects. LXDock files
are YML_ files and should define basic information allowing LXDock to properly create your
containers (eg. container names, images, ...). By default LXDock will try to use a file located
at ``./.lxdock.yml``.

.. _YML: http://yaml.org/

.. note::

  LXDock supports the following names for LXDock files: ``.lxdock.yml``, ``lxdock.yml``,
  ``.lxdock.yaml`` and ``lxdock.yaml``.

A container definition contains parameters that will be used when creating each container of a
specific project. It should be noted that most of the options that you can define in your LXDock
file can be applied "globally" or in the context of a specific container. For example you can define
a global ``image`` option telling to use the ``ubuntu/xenial`` for all your containers and decide to
use the ``debian/jessie`` image for a specific container:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  containers:
    - name: test01
    - name: test02
    - name: test03
      image: debian/jessie

This section contains a list of all configuration options supported by LXDock files.

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
LXDock will try to pull images from the default LXD's image server. So you can get a list of
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
scenario but you can manage your own image aliases and decide to use them with LXDock. You'll
need to use the ``mode: local`` option if you decide to do this (the default ``mode`` is ``pull``).
For example you could create an image associated with the ``old-ubuntu`` alias using:

.. code-block:: console

  $ lxc image copy ubuntu:12.04 local: --alias old-ubuntu

And then use it in your LXDock file as follows:

.. code-block:: yaml

  name: myproject
  image: old-ubuntu
  mode: local

mode
----

The ``mode`` option allows you to specify which mode to use in order to retrieve the images that
will be used to build your containers. Two values are allowed here: ``pull`` (which is the default
mode for LXDock) and ``local``. In ``pull`` mode container images will be pulled from an image
server (https://images.linuxcontainers.org/ by default). The ``local`` mode allows you to use local
container images (it can be useful if you decide to manage your own image aliases and want to use
them with LXDock).

name
----

This option can define the name of your project or the name of a container. In either cases, the
``name`` option is mandatory.

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  containers:
    - name: container01
    - name: container01

.. _conf-privileged:

privileged
----------

You should use the ``privileged`` option if you want to created privileged containers. Containers
created by LXDock are unprivileged by default. Such containers are safe by design because the root
user in the containers doesn't map to the host's root user: it maps to an unprivileged user
*outside* the container.

Here is an example on how to set up a privileged container in your LXDock file:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  containers:
    - name: web
      privileged: yes

.. note::

  Please refer to :doc:`glossary`  for more details on these notions.

protocol
--------

The ``protocol`` option defines which protocol to use when creating containers. By default LXDock
uses the ``simplestreams`` protocol (as the ``lxc`` command do) but you can change this to use the
``lxd`` protocol if you want. The ``simplestreams`` protocol is an image server description format,
using JSON to describe a list of images and allowing to get image information and import images.
The ``lxd`` protocol refers to the REST API that is used between LXD clients and LXD daemons.

provisioning
------------

The ``provisioning`` option allows you to define how to provision your containers as part of the
``lxdock up`` workflow. This provisioning can also be executed when running ``lxdock provision``.

The ``provisioning`` option should define a list of provisioning tools to execute. For example, it
can be an Ansible playbook to run:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  provisioning:
    - type: ansible
      playbook: deploy/site.yml

server
------

You can use this option to define which image server should be used to retrieve container images. By
default we are using https://images.linuxcontainers.org/.

shares
------

The ``shares`` option lets you define which folders on your host should be made available to your
containers (internally this feature uses lxc mounts). The ``shares`` option should define a list
of shared items. Each shared item should define a ``source`` (a path on your host system) and a
``dest`` (a destination path on your container filesystem). For example:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  shares:
    - source: /path/to/my/workspace/project/
      dest: /myshare

shell
-----

The ``shell`` option allows you to define the user to use when doing a ``lxdock shell``. This allows
you to have a shell for a specific user/home directory when doing ``lxdock shell``:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  shell:
    user: myuser
    home: /opt/myproject

users
-----

The ``users`` option allows you to define users that should be created by LXDock after creating a
container. This can be useful because the users created this way will automatically have read/write
permissions on shared folders. The ``users`` option should contain a list of users; each with a
``name`` and optionally a custom ``home`` directory or custom ``password``.

Passwords are encrypted using crypt(3) as explained in the useradd manpage, see ``man useradd``
for more information:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  users:
    - name: test01
    - name: test02
      home: /opt/test02
    - name: test03
      password: $6$cGzZBkDjOhGW$6C9wwqQteFEY4lQ6ZJBggE568SLSS7bIMKexwOD39mJQrJcZ5vIKJVIfwsKOZajhbPw0.Zqd0jU2NDLAnp9J/1
