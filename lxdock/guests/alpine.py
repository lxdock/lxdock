from .base import Guest


class AlpineGuest(Guest):
    """ This guest can provision Alpine containers. """

    name = 'alpine'
    barebones_packages = [
        'openssh',
        'python',
    ]

    def install_barebones_packages(self):
        """ Installs packages when the guest is first provisionned. """
        self.run(['apk', 'update'])
        self.run(['apk', 'add'] + self.barebones_packages)
        self.run(['rc-update', 'add', 'sshd'])
        self.run(['/etc/init.d/sshd', 'start'])
