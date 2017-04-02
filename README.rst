LXDock
######

.. image:: https://readthedocs.org/projects/lxdock/badge/?style=flat-square&version=stable
   :target: https://lxdock.readthedocs.io/en/stable/
   :alt: Documentation

.. image:: https://img.shields.io/pypi/l/lxdock.svg?style=flat-square
   :target: https://pypi.python.org/pypi/lxdock/
   :alt: License

.. image:: https://img.shields.io/pypi/v/lxdock.svg?style=flat-square
   :target: https://pypi.python.org/pypi/lxdock/
   :alt: Latest Version

.. image:: https://img.shields.io/travis/lxdock/lxdock.svg?style=flat-square
    :target: https://travis-ci.org/lxdock/lxdock
    :alt: Build status

.. image:: https://img.shields.io/codecov/c/github/lxdock/lxdock.svg?style=flat-square
    :target: https://codecov.io/github/lxdock/lxdock
    :alt: Codecov status

|

LXDock is a wrapper around LXD_ that allows developers to orchestrate their development environments
using a workflow similar to Vagrant.

.. contents:: Table of Contents
    :local:

Why use LXDock?
===============

**It's fast.** LXDock is much *much* faster than a typical Vagrant + Virtualbox setup.

**Multi-arch.** Vagrant has been designed with Virtualbox and x86 in mind. Even if you use
alternative providers, you're going to have to jump through inelegant hoops to have your
``Vagrantfile`` work on x86 and arm (for example) at the same time because the very concept of a
Vagrant box is arch-specific.

**Simpler.** When working with containers, much of the complexity of Vagrant becomes useless. Why
the need for special "vagrant-prepared" boxes when ``lxc exec`` is available? It's much simpler to
use whatever images are provided directly by lxd. By removing the need to manage boxes, ``lxdock``
suddenly becomes much simpler (a simple wrapper around lxd, really).

Documentation
=============

Online browsable documentation is available at https://lxdock.readthedocs.io.

Head over to the documentation for all the details on how to set up LXDock and how to start using
containers in your project!

Requirements
============

LXD_, Python 3.4+. Please refer to the requirements_ section of the documentation for a full list of
dependencies.

.. _LXD: https://www.ubuntu.com/cloud/lxd
.. _requirements: https://lxdock.readthedocs.io/en/stable/getting_started.html#requirements

Communication
=============

You can join the ``#lxdock`` channel on irc.freenode.net to get help and ask questions related to
the development of LXDock.

Authors
=======

Virgil Dupras (`@hsoft <https://github.com/hsoft>`_), Morgan Aubert
(`@ellmetha <https://github.com/ellmetha>`_) and contributors_.

.. _contributors: https://github.com/lxdock/lxdock/contributors

License
=======

GPLv3. See ``LICENSE`` for more details.
