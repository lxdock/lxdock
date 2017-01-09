Installation
============

Requirements
------------

- Python 3.4+
- A functional LXD_. You should be able to run ``lxc launch`` and have a container with an IPv4
  address running
- Proper permissions to run the ``lxc`` command. That usually means adding your user to the
  ``lxd`` group
- ``getfacl/setfacl`` if you use shared folders
- Ansible_

Is your lxd install working properly?
-------------------------------------

After you've installed LXD, you can verify that its nomad-ready with these commands:

.. code-block:: console

    $ lxc image copy images:debian/jessie local: --copy-aliases
    $ lxc image list
    +------------------------+--------------+--------+--------------------------------------+--------+---------+------------------------------+
    |         ALIAS          | FINGERPRINT  | PUBLIC |             DESCRIPTION              |  ARCH  |  SIZE   |         UPLOAD DATE          |
    +------------------------+--------------+--------+--------------------------------------+--------+---------+------------------------------+
    | debian/jessie (3 more) | 088459380bca | no     | Debian jessie amd64 (20161215_22:42) | x86_64 | 94.03MB | Dec 16, 2016 at 5:10pm (UTC) |
    +------------------------+--------------+--------+--------------------------------------+--------+---------+------------------------------+
    $ lxc launch local:debian/jessie thisisatest -c security.privileged=true
    Creating thisisatest
    Starting thisisatest
    $ lxc ls
    +------------------+---------+-----------------------+----------------------------------------------+------------+-----------+
    |       NAME       |  STATE  |         IPV4          |                     IPV6                     |    TYPE    | SNAPSHOTS |
    +------------------+---------+-----------------------+----------------------------------------------+------------+-----------+
    | thisisatest      | RUNNING | 10.104.153.175 (eth0) | fd42:383a:2f69:eaa0:216:3eff:fef8:aa0 (eth0) | PERSISTENT | 0         |
    +------------------+---------+-----------------------+----------------------------------------------+------------+-----------+
    $ ping -c 1 10.104.153.175
    PING 10.104.153.175 (10.104.153.175) 56(84) bytes of data.
    64 bytes from 10.104.153.175: icmp_seq=1 ttl=64 time=0.066 ms

    --- 10.104.153.175 ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 0.066/0.066/0.066/0.000 ms
    $ lxc stop thisisatest
    $ lxc delete thisisatest

If your output is similar, then you should be nomad-ready!

Installing LXD-Nomad itself
---------------------------

.. code-block:: console

    $ git clone https://github.com/lxd-nomad/lxd-nomad.git
    $ cd lxd-nomad
    $ pip3 install --user .
    $ nomad --version
    LXD-Nomad 0.2.0.dev

Alternatively, you can create yourself a virtualenv to install lxd-nomad in.

.. _LXD: https://linuxcontainers.org/lxd/
.. _Ansible: https://www.ansible.com/
