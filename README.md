# LXD-Nomad

[![Build Status](https://img.shields.io/travis/lxd-nomad/lxd-nomad.svg?style=flat-square&branch=master)](https://secure.travis-ci.org/lxd-nomad/lxd-nomad?branch=master)
[![Build Status](https://img.shields.io/codecov/c/github/lxd-nomad/lxd-nomad.svg?style=flat-square&branch=master)](https://codecov.io/github/lxd-nomad/lxd-nomad)

*LXD-Nomad* is a wrapper around [LXD][lxd] that allows a workflow similar to [Vagrant][vagrant].

## Why LXD-Nomad?

**It's fast.** LXD-Nomad is much *much* faster than a typical Vagrant + Virtualbox setup.

**Multi-arch.** Vagrant has been designed with Virtualbox and x86 in mind. Even if you use
alternative providers, you're going to have to jump through inelegant hoops to have your
`Vagrantfile` work on x86 and arm (for example) at the same time because the very concept of a
Vagrant box is arch-specific.

LXD transparently refers to containers of your native arch in the same namespace. Pulling
`debian/jessie` gets you an image of the proper arch whether you're on `x86_64` or `arm`.

**Simpler.** When working with containers, much of the complexity of Vagrant becomes useless. Why
the need for special "vagrant-prepared" boxes when `lxc exec` is available? It's much simpler to
use whatever images are provided directly by lxd. By removing the need to manage boxes, `nomad`
suddenly becomes much simpler (a simple wrapper around lxd, really).

## Status

Pretty usable, work in progress.

## Limitations

Except for the first one, all these limitations are temporary.

**Linux only.** LXD is a manager for Linux containers it only runs on Linux. It doesn't have a thin
VM layer like Docker has (yet?).

**Debian family guests.** So far, basic guest provisioning has been debian-centric.

**Ansible provisioning.** There isn't support for other provisioning tools yet.

## Documentation

Documentation about installation and usage is at https://lxd-nomad.readthedocs.io/en/latest/

[lxd]: https://linuxcontainers.org/lxd/
[vagrant]: https://www.vagrantup.com/
