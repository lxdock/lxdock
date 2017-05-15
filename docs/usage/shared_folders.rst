##############
Shared folders
##############

A common need when using a tool such as LXDock is to make some folders on your system available to
your containers. LXC/LXD provides a feature called "lxc mounts" - LXDock uses it internally in order
to provide support for "shared folders".

You can use the ``shares`` option in order to define which folders should be made available to your
containers. For example:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  shares:
    - source: /path/to/my/workspace/project/
      dest: /myshare

Of course you can associate many shared folders with your containers. In the previous example, the
content of the ``/path/to/my/workspace/project/`` on the host will be made available to the
container under the ``/myshare`` folder.

The problem with shared folder permissions
------------------------------------------

Shared folders in LXDock use lxc mounts. This is simple and fast, but there are problems with
permissions: shared folders means shared permissions. Changing permissions in the container means
changing them in the host as well, and vice versa. That leaves us with a problem that is tricky to
solve gracefully. Things become more complicated when our workflow has our container create files in
that shared folder. What permissions do we give these files?

LXDock tries to answer this by using ACLs. To ensure that files created by the container are
accessible to you back on the host (and vice versa), every new share has a default ACL giving the
current user full access to the source folder. An ACL is also added for the root user of the
container in order to allow him to access the shared folders on the guest side with read/write
permissions.

You should note that users created by your provisioning tools (eg. using Ansible) won't be able to
access your shares on the guest side. This is because LXDock has no knowledge of the users who
should have access to your shares. Moreover, your users/groups, when the container is initially
created, don't exist yet! That is why it does nothing. What is suggested is that you take care of it
in your own provisioning by setting up some ACLs. You can also make use of the ``users`` option
in order to force LXDock to create some users. The users created this way will be handled by LXDock
and will have read/write access to the shared folders:

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial

  shares:
    - source: /path/to/my/workspace/project/
      dest: /myshare

  users:
    - name: test01
    - name: test02
      home: /opt/test02

Disabling ACL support on shares
-------------------------------

By default ACLs will be turned on for all shares, however it is also possible to disable this
functionality on a per-share basis.  One reason you might want to do this, is when you are
using privileged containers and ensuring the container user matches the uid and gid
of the host system.  This allows a share to be mapped without the use of ACLs, however the
user should be aware of the security implications of making shares world-writable. This
may be acceptable for development only containers for example.

.. code-block:: yaml

  name: myproject
  image: ubuntu/xenial
  privileged: yes

  shares:
    - source: .
      dest: /myshare
      set_host_acl: false

  users:
    - name: test01

In this example, the Ansible provisioner can be used to change the uid and gid of
the test01 user after it has been created by LXDock. How to implement this is
up to the user, as LXDock does not provide a uid and gid option when creating users.
