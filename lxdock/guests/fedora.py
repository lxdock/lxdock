from .base import Guest


class FedoraGuest(Guest):
    """ This guest can provision Fedora containers. """

    name = 'fedora'
    barebones_packages = [
        'openssh-server',
        'python3',
    ]

    def install_barebones_packages(self):
        """ Installs packages when the guest is first provisionned. """
        self.run(['dnf', '-y', 'install', ] + self.barebones_packages)
