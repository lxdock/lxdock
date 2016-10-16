# vith: Vagrant Is Too Heavy

vith is a wrapper around lxd that allows a workflow similar to Vagrant.

## Status

Barely functional, work in progress.

## Requirements

* A functional LXD. You should be able to run `lxc launch` and have a container with an IPv4
  address running.
* Proper permissions to run the `lxc` command. That usually means adding your user to the `lxd`
  group.
* Local LXD images. Vith doesn't manage image copying. When you refer to `debian/jessie`, you need
  to have already coplied the image locally and properly aliased it.
* pylxd
* ansible

## Usage

It's not functional, so you can't use it, but if you put a `Vithfile.yml` somewhere that looks
like:

```
name: myproject
image: debian/jessie
provisioning:
  - type: ansible
    playbook: deploy/site.yml
```

... and that you have a pre-configured `jessie` container that works, you should be able to get
*something* out of `vith` commands made in the same folder.

## Why?

Vagrant has been designed with Virtualbox and x86 in mind. Yes, there are plugins like
`vagrant-lxc` that work quite well, but the main problem is when you try getting outside the x86
architecture. Vagrant boxes supports multiple providers, but not multiple arches.

To have a functional vagrant-based project tha can run, for example, on an ARM machine, you would
need to fudge your `Vagrantfile` to dynamically change the active box based on the current arch.

Also, when working with containers, much of the complexity of Vagrant becomes useless. Why
provision over SSH when you can use `lxc-attach`? Why fudge around with shared folders when mounting
a folder through lxc works so well? Why global box naming shemes when lxc supports containers in
any folder?
