#!/bin/bash

set -xe

# Install packages to use a virtualenv with python3
sudo -E apt-get -y install python3-setuptools python3-dev python3-virtualenv

# create a virtualenv and install lxdock
python3 -m virtualenv -p python3 ~/venv
source ~/venv/bin/activate

cd /vagrant
# Clean local builds to enable fresh build inside the Vagrant box
make clean
make install

# automatically activate virtualenv and switch to /vagrant on login
echo "source ~/venv/bin/activate" >> ~/.bashrc
echo "cd /vagrant" >> ~/.bashrc
