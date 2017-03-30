from .base import Guest


class OracleLinuxGuest(Guest):
    """ This guest can provision Oracle Linux containers. """

    name = 'ol'
    ansible_packages = [
        'openssh-server',
        'python',
    ]

    def install_ansible_packages(self):
        self.run(['yum', '-y', 'install'] + self.ansible_packages)
