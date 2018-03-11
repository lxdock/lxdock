#!/bin/bash

set -xe

# python3-virtualenv is not available on Trusty so install it here
sudo -E apt-get -y install python3-setuptools python3-dev python3-virtualenv

# create a virtualenv and install lxdock
python3 -m virtualenv -p python3 ~/venv
source ~/venv/bin/activate
cd /vagrant
make install

# automatically activate virtualenv and switch to /vagrant on login
echo "source ~/venv/bin/activate" >> ~/.bashrc
echo "cd /vagrant" >> ~/.bashrc
