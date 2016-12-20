# LXD-Nomad

[![Build Status](https://img.shields.io/travis/lxd-nomad/lxd-nomad.svg?style=flat-square&branch=master)](https://secure.travis-ci.org/lxd-nomad/lxd-nomad?branch=master)
[![Build Status](https://img.shields.io/codecov/c/github/lxd-nomad/lxd-nomad.svg?style=flat-square&branch=master)](https://codecov.io/github/lxd-nomad/lxd-nomad)

*LXD-Nomad* is a wrapper around lxd that allows a workflow similar to Vagrant.

## Status

Barely functional, work in progress.

## Requirements

* Python 3.4+
* A functional LXD. You should be able to run `lxc launch` and have a container with an IPv4
  address running
* Proper permissions to run the `lxc` command. That usually means adding your user to the `lxd`
  group
* `getfacl/setfacl` if you use shared folders
* ansible

### Is your lxd install working properly?

After you've installed LXD, you can verify that its nomad-ready with these commands:

```
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
```

If your output is similar, then you should be nomad-ready!

## Installation

```
$ git clone https://github.com/lxd-nomad/lxd-nomad.git
$ cd lxd-nomad
$ pip3 install --user .
$ nomad --version
LXD-Nomad 0.2.0.dev
```

Alternatively, you can create yourself a virtualenv to install lxd-nomad in.

## Usage

It's barely functional, but if you put a `.nomad.yml` somewhere that looks like:

```
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
```

... and that you have a pre-configured `jessie` container that works, you should manage to get
a workflow similar to Vagrant's.

```
$ nomad up
[ lot's of output because the conatiner is provisioned]
$ curl http://myproject.local
$ nomad shell
# echo "in my container!"
# exit
$ nomad halt
```

It should be noted that the `image` value can also contain a name of a container alias that
includes the targetted architecture (eg. `debian/jessie/amd64` or `ubuntu/xenial/armhf`). The
image will be pulled from the https://images.linuxcontainers.org/ image server by default (so you
can get a list of supported aliases by using the `lxc image alias list images:` command). You can
also choose to use another server by manually setting the `server` value.

## Multiple containers

You can define multiple containers in your `.nomad.yml` file.

```
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

```

If you define some global values (eg. `images`, `mode` or `provision`) outside of the scope of the
`containers` block, these values will be used when creating each container unless you re-define them
in the container's configuration scope.

## Privileged containers

There seems to be some problems with containers running systemd-based systems. Their init system
seem broken. You can confirm this by trying to `exec bash` into the container and try to execute
`systemctl`. If you get a dbus-related error, then yup, your container is broken and you need to
run the container as privileged.

## Shared folders and ACL

Shared folders in LXD-Nomad use lxc mounts. This is simple and fast, but there are problems with
permissions: shared folders means shared permissions. Changing permissions in the container means
changing them in the host as well, and vice versa. That leaves us with a problem that is tricky
to solve gracefully. Things become more complicated when our workflow has our container create
files in that shared folder. What permissions do we give these files?

For now, the best solution we could come up with is to use ACLs. To ensure that files created
by the container are accessible to you back on the host, every new share has a default ACL giving
the current user full access to the source folder (`setfacl -Rdm u:<your uid>:rwX <shared source>`).

On the guest side, it's more tricky. LXD-nomad has no knowledge of the users who should have
access to your shares. Moreover, your users/groups, when the container is initially created, don't
exist yet! That is why it does nothing. What is suggested is that you take care of it in your own
provisioning. Here's what it could look like:

```
- acl: name=/myshare entity=myuser etype=user permissions=rwX state=present
```

## Why LXD-Nomad?

Vagrant has been designed with Virtualbox and x86 in mind. Yes, there are plugins like
`vagrant-lxc` that work quite well, but the main problem is when you try getting outside the x86
architecture. Vagrant boxes supports multiple providers, but not multiple arches.

To have a functional vagrant-based project tha can run, for example, on an ARM machine, you would
need to fudge your `Vagrantfile` to dynamically change the active box based on the current arch.

Also, when working with containers, much of the complexity of Vagrant becomes useless. Why
the need for special "vagrant-prepared" boxes when `lxc exec` is available? It's much simpler to
use whatever images are provided directly by lxd. By removing the need to manage boxes, `nomad`
suddenly becomes much simpler (a simple wrapper around lxd, really).
