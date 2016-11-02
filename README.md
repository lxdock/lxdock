# LXD-Nomad

*LXD-Nomad* is a wrapper around lxd that allows a workflow similar to Vagrant.

## Status

Barely functional, work in progress.

## Requirements

* A functional LXD. You should be able to run `lxc launch` and have a container with an IPv4
  address running.
* Proper permissions to run the `lxc` command. That usually means adding your user to the `lxd`
  group.
* Local LXD images. *LXD-Nomad* doesn't manage image copying. When you refer to `debian/jessie`, you need
  to have already coplied the image locally and properly aliased it.
* `getfacl/setfacl` if you use shared folders.
* pylxd
* ansible

## Usage

It's not functional, so you can't use it, but if you put a `.nomad.yml` somewhere that looks
like:

```
name: myproject
image: debian/jessie
privileged: true # jessie is systemd
hostnames:
  - myproject.local
shares:
  - source: .
    dest: /myshare
provisioning:
  - type: ansible
    playbook: deploy/site.yml
```

... and that you have a pre-configured `jessie` container that works, you should be able to get
*something* out of `nomad` commands made in the same folder.

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
