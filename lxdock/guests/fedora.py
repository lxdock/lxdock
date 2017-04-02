from .base import Guest


class FedoraGuest(Guest):
    """ This guest can provision Fedora containers. """

    name = 'fedora'

    def install_packages(self, packages):
        self.run(['dnf', '-y', 'install', ] + packages)
