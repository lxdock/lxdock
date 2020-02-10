#######
Puppet
#######

LXDock provides built-in support for `Puppet`_ provisioning.

.. _Puppet: https://puppet.com/


Distribution Support
--------------------

Puppet provisioning requires the executable ``puppet`` in the guest container. For ArchLinux,
Debian, Fedora and Ubuntu guests, LXDock tries to install the ``puppet`` package during
``lxdock up``.

However, the automatic installation may fail, it may install an old version of Puppet, or you
may also use another Linux distribution. In these cases, you may see an error message at
the beginning of ``lxdock provision`` or during the provisioning (due to version mismatch).
You will have to check out the proper documentation for your Linux distribution and Puppet version,
and add a shell provisioner in LXDock file before the Puppet provisioner. Here is an example for
CentOS 7:

.. code-block:: yaml

  name: centos-7
  image: centos/7

  provisioning:
    - type: shell
      inline: sh -c 'rpm -ivh https://yum.puppetlabs.com/puppetlabs-release-el-7.noarch.rpm && yum -y install puppet'
    - type: puppet
      [...] # Puppet options

By default, LXDock runs ``which puppet`` to find the executable. You may override this behavior
by providing ``binary_path`` option and LXDock will then find ``puppet`` executable under that path.


Usage
-----

Add a ``puppet`` provisioning operation to your LXDock file as follows:

.. code-block:: yaml

  name: myproject
  image: ubuntu/bionic

  provisioning:
    - type: puppet
      manifests_path: manifests
      manifest_file: site.pp
      module_path: modules
      hiera_config_path: hiera.yaml
      facter:
          role: app
          domain_name: app.example.com
      options: "--verbose --debug"


Puppet provisioning can be run in "manifest" mode or "environment" mode by setting ``manifests_path``
or ``environment_path``, respectively. If ``manifest_file`` is not provided in "manifest" mode, it is
given the default value ``default.pp``. If ``environment`` is not provided in "environment" mode, it
is given ``production`` as the default value.

If none of ``manifests_path`` and ``environment_path`` are given, LXDock assumes "manifest" mode and
set ``manifests_path`` to ``manifests``. During the validation of an LXDock file, the existence of
``manifests_path/manifest_file`` or ``environment_path/environment`` is checked.


Options
-------

LXDock's Puppet provisioning is expected to reuse the files and configurations for a Vagrant project.
This is still experimental, so if it doesn't work for your case, please feel free to create a GitHub
issue!

Here are the options that LXDock has supported:

- ``binary_path``
- ``facter``
- ``hiera_config_path``
- ``manifest_file``
- ``manifests_path``
- ``module_path``
- ``environment``
- ``environment_path``
- ``environment_variables``
- ``options``: LXDock takes a single string of space-separated options, instead of an array of strings.

Please reference: `Vagrant docs`_

.. _Vagrant docs: https://www.vagrantup.com/docs/provisioning/puppet_apply.html#options
