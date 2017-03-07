from .base import Guest


class OpenSUSEGuest(Guest):
    """ This guest can provision openSUSE containers. """

    name = 'opensuse'
    barebones_packages = [
        'openSSH',
        'python3-base',
    ]

    def install_barebones_packages(self):
        """ Installs packages when the guest is first provisionned. """
        self.run(['zypper', '--non-interactive', 'install', ] + self.barebones_packages)
