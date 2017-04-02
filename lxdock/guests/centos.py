from .base import Guest


class CentosGuest(Guest):
    """ This guest can provision Centos containers. """

    name = 'centos'

    def install_packages(self, packages):
        self.run(['yum', '-y', 'install'] + packages)
