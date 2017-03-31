import logging
import subprocess
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
        """ Performs the provisioning operations using the considered provisioner. """
        ip = get_ipv4_ip(self.lxd_container)
        with tempfile.NamedTemporaryFile() as tmpinv:
            tmpinv.write('{} ansible_user=root'.format(ip).encode('ascii'))
            tmpinv.flush()
            cmd = self._build_ansible_playbook_command(tmpinv.name)
            logger.debug(cmd)
            p = subprocess.Popen(cmd, shell=True)
            p.wait()

    def _build_ansible_playbook_command(self, inventory_filename):
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
        return ' '.join(cmd_args)
