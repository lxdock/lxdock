from .base import Guest


class DebianGuest(Guest):
    """ This guest can provision Debian containers. """

    name = 'debian'
    barebones_packages = [
        'apt-utils',
        'aptitude',
        'openssh-server',
        'python',
    ]

    def install_barebones_packages(self):
        """ Installs packages when the guest is first provisionned. """
        self.run(['apt-get', 'install', '-y'] + self.barebones_packages)
