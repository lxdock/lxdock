from .base import Guest


class DebianGuest(Guest):
    """ This guest can provision Debian containers. """

    name = 'debian'

    def install_packages(self, packages):
        self.run(['apt-get', 'install', '-y'] + packages)
