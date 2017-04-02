from .base import Guest


class AlpineGuest(Guest):
    """ This guest can provision Alpine containers. """

    name = 'alpine'

    def install_packages(self, packages):
        self.run(['apk', 'update'])
        self.run(['apk', 'add'] + packages)
