from .base import Guest


class CentosGuest(Guest):
    """ This guest can provision Centos containers. """

    name = 'centos'
    ansible_packages = [
        'openssh-server',
        'python',
    ]

    def install_ansible_packages(self):
        self.run(['yum', '-y', 'install'] + self.ansible_packages)
