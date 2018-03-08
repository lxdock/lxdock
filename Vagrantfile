# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
python3 -m virtualenv -p python3 ~/venv
echo "source ~/venv/bin/activate" >> ~/.bashrc
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.provision "shell", path: "scripts/ci-base-setup.sh", privileged: false
  config.vm.provision "shell", inline: $script, privileged: false
end
