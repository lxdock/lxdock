import logging
import tempfile

from voluptuous import Extra, IsFile, Required

from ..network import get_ip
from .base import Provisioner


logger = logging.getLogger(__name__)


class AnsibleProvisioner(Provisioner):
    """ Allows to perform provisioning operations using Ansible. """

    name = 'ansible'

    guest_required_packages_alpine = ['python', ]
    guest_required_packages_arch = ['python', ]
    guest_required_packages_centos = ['python', ]
    guest_required_packages_debian = ['apt-utils', 'aptitude', 'python', ]
    guest_required_packages_fedora = ['python2', ]
    guest_required_packages_gentoo = ['dev-lang/python', ]
    guest_required_packages_opensuse = ['python3-base', ]
    guest_required_packages_ol = ['python', ]
    guest_required_packages_ubuntu = ['apt-utils', 'aptitude', 'python', ]

    schema = {
        Required('playbook'): IsFile(),
        'ask_vault_pass': bool,
        'vault_password_file': IsFile(),
        'groups': {Extra: [str, ]},
        'lxd_transport': bool,
    }

    def get_inventory(self):
        def line(guest):
            if self.options.get('lxd_transport'):
                ip = guest.container.lxd_name
            else:
                ip = get_ip(guest.lxd_container)
            return '{} ansible_host={} ansible_user=root'.format(guest.container.name, ip)

        def fmtgroup(name, hosts):
            hosts = [host for host in hosts if host in guestnames]
            return '[{}]\n{}'.format(name, '\n'.join(hosts))

        all_hosts_lines = '\n'.join(line(guest) for guest in self.guests)
        groups = self.options.get('groups', {})
        guestnames = {guest.container.name for guest in self.guests}
        groups_lines = '\n\n'.join(fmtgroup(key, val) for key, val in groups.items())
        return '\n\n'.join([all_hosts_lines, groups_lines])

    def provision(self):
        """ Performs the provisioning operations using ansible-playbook. """
        self.setup()
        with tempfile.NamedTemporaryFile() as tmpinv:
            tmpinv.write(self.get_inventory().encode('ascii'))
            tmpinv.flush()
            self.host.run(self._build_ansible_playbook_command_args(tmpinv.name))

    def setup_single(self, guest):
        super().setup_single(guest)

        if self.options.get('lxd_transport'):
            # we don't need ssh
            return

        ssh_pkg_name = {
            'alpine': 'openssh',
            'arch': 'openssh',
            'gentoo': 'net-misc/openssh',
            'opensuse': 'openSSH',
        }.get(guest.name, 'openssh-server')
        guest.install_packages([ssh_pkg_name])

        # Make sure that sshd is started
        if guest.name == 'alpine':
            guest.run(['rc-update', 'add', 'sshd'])
            guest.run(['/etc/init.d/sshd', 'start'])
        elif guest.name in {'arch', 'centos', 'fedora'}:
            guest.run(['systemctl', 'enable', 'sshd'])
            guest.run(['systemctl', 'start', 'sshd'])
        elif guest.name == 'ol':
            guest.run(['/sbin/service', 'sshd', 'start'])

        # Add the current user's SSH pubkey to the container's root SSH config.
        ssh_pubkey = self.host.get_ssh_pubkey()
        if ssh_pubkey is not None:
            guest.add_ssh_pubkey_to_root_authorized_keys(ssh_pubkey)
        else:
            logger.warning('SSH pubkey was not found. Provisioning tools may not work correctly...')

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

        if self.options.get('lxd_transport'):
            cmd_args.extend(['-c', 'lxd', ])

        # Append the playbook filepath and return the final command.
        cmd_args.append(self.homedir_expanded_path(self.options['playbook']))
        return cmd_args
