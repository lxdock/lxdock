import logging
import tempfile

from voluptuous import IsFile, Required

from ..network import get_ipv4_ip

from .base import Provisioner

logger = logging.getLogger(__name__)


class AnsibleProvisioner(Provisioner):
    """ Allows to perform provisioning operations using Ansible. """

    name = 'ansible'
    schema = {
        Required('playbook'): IsFile(),
        'ask_vault_pass': bool,
        'vault_password_file': IsFile(),
    }

    def provision(self):
        """ Performs the provisioning operations using ansible-playbook. """
        ip = get_ipv4_ip(self.guest.lxd_container)
        with tempfile.NamedTemporaryFile() as tmpinv:
            tmpinv.write('{} ansible_user=root'.format(ip).encode('ascii'))
            tmpinv.flush()
            self.host.run(self._build_ansible_playbook_command_args(tmpinv.name))

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
