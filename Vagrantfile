# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrant file to setup a vagrant box for running lxdock tests locally,
# requires Vagrant 1.8.5+ for the bento image. Run "make coverage" inside box.

$script = <<SCRIPT
sudo apt-get -y install python3-virtualenv
python3 -m virtualenv -p python3 ~/venv
source ~/venv/bin/activate
cd /vagrant
make install
echo "source ~/venv/bin/activate" >> ~/.bashrc
echo "cd /vagrant" >> ~/.bashrc
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.provision "shell", inline: "cd /vagrant; make test-setup", privileged: false
  config.vm.provision "shell", inline: $script, privileged: false
end
