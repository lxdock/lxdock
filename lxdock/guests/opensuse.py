from .base import Guest


class OpenSUSEGuest(Guest):
    """ This guest can provision openSUSE containers. """

    name = 'opensuse'

    def install_packages(self, packages):
        self.run(['zypper', '--non-interactive', 'install', ] + packages)
