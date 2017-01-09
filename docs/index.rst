LXD-Nomad: because Vagrant is too heavy
=======================================

.. This is a verbatim copy of the README. Sure, it's annoying to have to keep them in sync, but
   the content should stabilize at some point and we won't have to sync it very often anymore.

*LXD-Nomad* is a wrapper around LXD_ that allows a workflow similar to Vagrant_.

Why LXD-Nomad?
--------------

**It's fast.** LXD-Nomad is much *much* faster than a typical Vagrant + Virtualbox setup.

**Multi-arch.** Vagrant has been designed with Virtualbox and x86 in mind. Even if you use
alternative providers, you're going to have to jump through inelegant hoops to have your
``Vagrantfile`` work on x86 and arm (for example) at the same time because the very concept of a
Vagrant box is arch-specific.

LXD transparently refers to containers of your native arch in the same namespace. Pulling
``debian/jessie`` gets you an image of the proper arch whether you're on ``x86_64`` or ``arm``.

**Simpler.** When working with containers, much of the complexity of Vagrant becomes useless. Why
the need for special "vagrant-prepared" boxes when ``lxc exec`` is available? It's much simpler to
use whatever images are provided directly by lxd. By removing the need to manage boxes, ``nomad``
suddenly becomes much simpler (a simple wrapper around lxd, really).

Status
------

Pretty usable, work in progress.

Limitations
-----------

Except for the first one, all these limitations are temporary.

**Linux only.** LXD is a manager for Linux containers it only runs on Linux. It doesn't have a thin
VM layer like Docker has (yet?).

**Debian family guests.** So far, basic guest provisioning has been debian-centric.

**Ansible provisioning.** There isn't support for other provisioning tools yet.

Contents
--------

.. toctree::
   :maxdepth: 2

   user/install
   user/usage

.. _LXD: https://linuxcontainers.org/lxd/
.. _Vagrant: https://www.vagrantup.com/
