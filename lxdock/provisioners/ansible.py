import logging
import tempfile

from voluptuous import IsFile, Required

from ..network import get_ip
from .base import Provisioner


logger = logging.getLogger(__name__)


class AnsibleProvisioner(Provisioner):
    """ Allows to perform provisioning operations using Ansible. """

    name = 'ansible'

    guest_required_packages_alpine = ['openssh', 'python', ]
    guest_required_packages_arch = ['openssh', 'python', ]
    guest_required_packages_centos = ['openssh-server', 'python', ]
    guest_required_packages_debian = ['apt-utils', 'aptitude', 'openssh-server', 'python', ]
    guest_required_packages_fedora = ['openssh-server', 'python2', ]
    guest_required_packages_gentoo = ['net-misc/openssh', 'dev-lang/python', ]
    guest_required_packages_opensuse = ['openSSH', 'python3-base', ]
    guest_required_packages_ol = ['openssh-server', 'python', ]
    guest_required_packages_ubuntu = ['apt-utils', 'aptitude', 'openssh-server', 'python', ]

    schema = {
        Required('playbook'): IsFile(),
        'ask_vault_pass': bool,
        'vault_password_file': IsFile(),
    }

    def get_inventory(self, guests):
        def line(guest):
            ip = get_ip(guest.lxd_container)
            return '{} ansible_user=root'.format(ip)

        return '\n'.join(line(guest) for guest in guests)

    def provision(self):
        """ Performs the provisioning operations using ansible-playbook. """
        self.setup()
        with tempfile.NamedTemporaryFile() as tmpinv:
            tmpinv.write(self.get_inventory(self.guests).encode('ascii'))
            tmpinv.flush()
            self.host.run(self._build_ansible_playbook_command_args(tmpinv.name))

    def setup_single(self, guest):
        super().setup_single(guest)

        # Add the current user's SSH pubkey to the container's root SSH config.
        ssh_pubkey = self.host.get_ssh_pubkey()
        if ssh_pubkey is not None:
            guest.add_ssh_pubkey_to_root_authorized_keys(ssh_pubkey)
        else:
            logger.warning('SSH pubkey was not found. Provisioning tools may not work correctly...')

    def setup_guest_alpine(self, guest):
        # On alpine guests we have to ensure that ssd is started!
        guest.run(['rc-update', 'add', 'sshd'])
        guest.run(['/etc/init.d/sshd', 'start'])

    def setup_guest_arch(self, guest):
        # On archlinux guests we have to ensure that sshd is started!
        guest.run(['systemctl', 'enable', 'sshd'])
        guest.run(['systemctl', 'start', 'sshd'])

    def setup_guest_centos(self, guest):
        # On centos guests we have to ensure that sshd is started!
        guest.run(['systemctl', 'enable', 'sshd'])
        guest.run(['systemctl', 'start', 'sshd'])

    def setup_guest_fedora(self, guest):
        # On fedora guests we have to ensure that sshd is started!
        guest.run(['systemctl', 'enable', 'sshd'])
        guest.run(['systemctl', 'start', 'sshd'])

    def setup_guest_ol(self, guest):
        # On oracle linux guests we have to ensure that sshd is started!
        guest.run(['/sbin/service', 'sshd', 'start'])

    ##################################
    # PRIVATE METHODS AND PROPERTIES #
    ##################################

    def _build_ansible_playbook_command_args(self, inventory_filename):
        cmd_args = ['ANSIBLE_HOST_KEY_CHECKING=False', 'ansible-playbook', ]
        cmd_args.extend(['--inventory-file', inventory_filename, ])

        # Append the --ask-vault-pass option if applicable.
        if self.options.get('ask_vault_pass'):
            cmd_args.append('--ask-vault-pass')

        # Append the --vault-password-file option if applicable.
        vault_password_file = self.options.get('vault_password_file')
        if vault_password_file is not None:
            cmd_args.extend([
                '--vault-password-file', self.homedir_expanded_path(vault_password_file)])

        # Append the playbook filepath and return the final command.
        cmd_args.append(self.homedir_expanded_path(self.options['playbook']))
        return cmd_args
