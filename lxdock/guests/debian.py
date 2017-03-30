from .base import Guest


class DebianGuest(Guest):
    """ This guest can provision Debian containers. """

    name = 'debian'
    ansible_packages = [
        'apt-utils',
        'aptitude',
        'openssh-server',
        'python',
    ]

    def install_ansible_packages(self):
        self.run(['apt-get', 'install', '-y'] + self.ansible_packages)
