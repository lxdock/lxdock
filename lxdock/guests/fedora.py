from .base import Guest


class FedoraGuest(Guest):
    """ This guest can provision Fedora containers. """

    name = 'fedora'
    ansible_packages = [
        'openssh-server',
        'python3',
    ]

    def install_ansible_packages(self):
        self.run(['dnf', '-y', 'install', ] + self.ansible_packages)
