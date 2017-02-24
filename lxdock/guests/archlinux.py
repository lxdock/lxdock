from .base import Guest


class ArchLinuxGuest(Guest):
    """ This guest can provision ArchLinux containers. """

    name = 'arch'
    barebones_packages = [
        'openssh',
        'python2',
    ]

    def install_barebones_packages(self):
        """ Installs packages when the guest is first provisionned. """
        self.run(['pacman', '-S', '--noconfirm'] + self.barebones_packages)
