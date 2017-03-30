from .base import Guest


class OpenSUSEGuest(Guest):
    """ This guest can provision openSUSE containers. """

    name = 'opensuse'
    ansible_packages = [
        'openSSH',
        'python3-base',
    ]

    def install_ansible_packages(self):
        self.run(['zypper', '--non-interactive', 'install', ] + self.ansible_packages)
