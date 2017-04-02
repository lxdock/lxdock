from .base import Guest


class ArchLinuxGuest(Guest):
    """ This guest can provision ArchLinux containers. """

    name = 'arch'

    def install_packages(self, packages):
        self.run(['pacman', '-S', '--noconfirm'] + packages)
