from .base import Guest


class AlpineGuest(Guest):
    """ This guest can provision Alpine containers. """

    name = 'alpine'
    ansible_packages = [
        'openssh',
        'python',
    ]

    def install_ansible_packages(self):
        self.run(['apk', 'update'])
        self.run(['apk', 'add'] + self.ansible_packages)
        self.run(['rc-update', 'add', 'sshd'])
        self.run(['/etc/init.d/sshd', 'start'])
