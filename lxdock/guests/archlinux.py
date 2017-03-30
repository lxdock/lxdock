from .base import Guest


class ArchLinuxGuest(Guest):
    """ This guest can provision ArchLinux containers. """

    name = 'arch'
    ansible_packages = [
        'openssh',
        'python2',
    ]

    def install_ansible_packages(self):
        self.run(['pacman', '-S', '--noconfirm'] + self.ansible_packages)
