Glossary
========

This is a comprehensive list of the terms used when discussing the functionality and the
configuration options of LXDock.

.. glossary::
    :sorted:

    Container
        Or *Linux containers*. Whenever we use the term "container", we are referring to LXD
        containers. LXD focuses on system containers / infrastructure containers and thus provides
        an elegant solution to the problem of how to reliably run software in multiple computing
        environments (eg. for development or tests execution).

    Image
        An image (or container image) is necessary to build a container. Basically container
        images embed a snapshot of a full filesystem and some configuration-related tools. All
        containers are built from "local" images; but images can also be pulled from a remote image
        server (the default LXD's image server is at https://images.linuxcontainers.org/). This a
        good option because users don't have to manage their own images but they have to trust the
        image server they are using!

    LXC
        LXC stands for "Linux containers". It is a technology that allows to virtualize software
        (which can be an entire operating system) at the operating system level, within the Linux
        kernel.

    LXD
        LXD can be seen as an extension of LXC. It's a container system that makes use of LXC. It
        provides many tools built around LXC such as a REST API to interact with your containers, an
        intuitive command line tool, a container image system, ...

    Privileged container
        Privileged containers are containers where the root user (in the container) is mapped to the
        host's root user. This is not really "root-safe" and could lead to potential security
        flaws. That said it should be noted that privileged containers come with some protection
        mechanisms in order to protect the host. You can refer to `LXC's documentation
        <https://linuxcontainers.org/fr/lxc/security/>`_ for more details on this topic.

    Unprivileged container
        Unprivileged containers are containers where the root user (in the container) is mapped to
        an unprivileged container on the host. So the user that corresponds to the container's root
        user only has advanced rights and permissions on the resources related to the container it
        is associated to.
