# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrant file to setup a vagrant box for running lxdock tests locally,
# requires Vagrant 1.8.5+ for the bento image. Run "make coverage" inside box.

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.provision "shell", path: "scripts/ci-base-setup.sh", privileged: false
  config.vm.provision "shell", path: "scripts/vagrant-base-setup.sh", privileged: false
end
