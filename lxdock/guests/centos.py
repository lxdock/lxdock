from .base import Guest


class CentosGuest(Guest):
    """ This guest can provision Centos containers. """

    name = 'centos'
    barebones_packages = [
        'openssh-server',
        'python',
    ]

    def install_barebones_packages(self):
        """ Installs packages when the guest is first provisionned. """
        self.run(['yum', '-y', 'install'] + self.barebones_packages)
