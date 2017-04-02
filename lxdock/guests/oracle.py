from .base import Guest


class OracleLinuxGuest(Guest):
    """ This guest can provision Oracle Linux containers. """

    name = 'ol'

    def install_packages(self, packages):
        self.run(['yum', '-y', 'install'] + packages)
