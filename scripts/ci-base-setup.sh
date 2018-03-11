#!/bin/bash

set -xe

sudo -E apt-get purge -y lxd lxd-client
sudo -E apt-get install -y snapd python3-setuptools python3-dev python3-virtualenv
sudo snap install lxd
sudo snap list
sudo lxd --version

export PATH="/snap/bin:$PATH"

# lxd waitready times out
while [ ! -S /var/snap/lxd/common/lxd/unix.socket ]; do
  sleep 0.5
done

user=`whoami`
sudo usermod -a -G lxd $user

sudo lxd init --auto
sudo lxc network create lxdbr0 ipv6.address=none ipv4.address=10.0.3.1/24 ipv4.nat=true
sudo lxc network attach-profile lxdbr0 default eth0

# ansible test needs ssh
if [ ! -f $HOME/.ssh/id_rsa ]; then
  ssh-keygen -t rsa -b 2048 -f $HOME/.ssh/id_rsa -P ""
fi
