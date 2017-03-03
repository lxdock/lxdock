###################
Multiple containers
###################

You can define multiple containers in your LXDock file. All you have to do is to use the
``containers`` section and define your containers below it.

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

If you define some global values (eg. ``images``, ``mode`` or ``provision``) outside of the scope of
the ``containers`` block, these values will be used when creating each container unless you
re-define them in the container's configuration scope.
