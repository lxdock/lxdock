Usage
=====

We don't have proper documentation yet, but if you put a ``.nomad.yml`` somewhere that looks like:

.. code-block:: yaml

    name: myproject
    image: debian/jessie
    mode: pull # with this mode, debian/jessie is automatically pulled from LXD's public images repo
    privileged: true # jessie is systemd

    # Those hostnames will be bound to the container's IP in your host's /etc/hosts file
    hostnames:
      - myproject.local

    # Will mount the project's root folder to /myshare in the container
    shares:
      - source: .
        dest: /myshare

    # When doing "nomad shell", you'll be having a shell for the specified user/home
    shell:
      user: deployuser
      home: /opt/myproject

    # Upon our first "nomad up", this ansible playbook will be ran from the host with the container's
    # IP in the inventory.
    provisioning:
      - type: ansible
        playbook: deploy/site.yml

... you should manage to get a workflow similar to Vagrant's.

.. code-block:: console

    $ nomad up
    [ lot's of output because the container is provisioned]
    $ curl http://myproject.local
    $ nomad shell
    # echo "in my container!"
    # exit
    $ nomad halt

It should be noted that the ``image`` value can also contain a name of a container alias that
includes the targetted architecture (eg. ``debian/jessie/amd64`` or ``ubuntu/xenial/armhf``). The
image will be pulled from the <https://images.linuxcontainers.org/> image server by default (so you
can get a list of supported aliases by using the ``lxc image alias list images:`` command). You can
also choose to use another server by manually setting the ``server`` value.

Multiple containers
-------------------

You can define multiple containers in your ``.nomad.yml`` file.

.. code-block:: yaml

    image: ubuntu/xenial
    mode: pull

    containers:
      - name: web
        hostnames:
          - myproject.local

      - name: ci
        image: debian/jessie
        privileged: true
        hostnames:
          - ci.local


If you define some global values (eg. ``images``, ``mode`` or ``provision``) outside of the scope
of the ``containers`` block, these values will be used when creating each container unless you
re-define them in the container's configuration scope.

Privileged containers
---------------------

There seems to be some problems with containers running systemd-based systems. Their init system
seem broken. You can confirm this by trying to ``exec bash`` into the container and try to execute
``systemctl``. If you get a dbus-related error, then yup, your container is broken and you need to
run the container as privileged.

Shared folders and ACL
----------------------

Shared folders in LXD-Nomad use lxc mounts. This is simple and fast, but there are problems with
permissions: shared folders means shared permissions. Changing permissions in the container means
changing them in the host as well, and vice versa. That leaves us with a problem that is tricky
to solve gracefully. Things become more complicated when our workflow has our container create
files in that shared folder. What permissions do we give these files?

For now, the best solution we could come up with is to use ACLs. To ensure that files created
by the container are accessible to you back on the host, every new share has a default ACL giving
the current user full access to the source folder (``setfacl -Rdm u:<your uid>:rwX <shared source>``).

On the guest side, it's more tricky. LXD-nomad has no knowledge of the users who should have
access to your shares. Moreover, your users/groups, when the container is initially created, don't
exist yet! That is why it does nothing. What is suggested is that you take care of it in your own
provisioning. Here's what it could look like:

.. code-block:: yaml

    - acl: name=/myshare entity=myuser etype=user permissions=rwX state=present

Tired of sudoing for hostname bindings?
---------------------------------------

Every time a ``nomad up`` or ``nomad halt`` is made, we mangle ``/etc/hosts`` to make our configured
hostname bindings work. In a typical setup, your user doesn't have write access to that file. This
means that lxd-nomad requires you to type your sudo password all the time. If you're tired of that,
give your user write access to ``/etc/hosts``. Sure, there are some security implications in doing
that, but on a typical developer box and in this HTTPS Everywhere world, the risk ain't that great.
