import re
import unittest.mock

from lxdock.guests import AlpineGuest, DebianGuest
from lxdock.hosts import Host
from lxdock.provisioners import AnsibleProvisioner


class TestAnsibleProvisioner:
    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_ansible_playbooks(self, mock_popen):
        host = Host(unittest.mock.Mock())
        guest = DebianGuest(unittest.mock.Mock())
        lxd_state = unittest.mock.Mock()
        lxd_state.network.__getitem__ = unittest.mock.MagicMock(
            return_value={'addresses': [{'family': 'init', 'address': '0.0.0.0', }, ]})
        guest.lxd_container.state.return_value = lxd_state
        provisioner = AnsibleProvisioner('./', host, guest, {'playbook': 'deploy.yml'})
        provisioner.provision()
        assert re.match(
            'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --inventory-file /[/\w]+ '
            './deploy.yml', mock_popen.call_args[0][0])

    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_ansible_playbooks_with_the_vault_password_file_option(self, mock_popen):
        host = Host(unittest.mock.Mock())
        guest = DebianGuest(unittest.mock.Mock())
        lxd_state = unittest.mock.Mock()
        lxd_state.network.__getitem__ = unittest.mock.MagicMock(
            return_value={'addresses': [{'family': 'init', 'address': '0.0.0.0', }, ]})
        guest.lxd_container.state.return_value = lxd_state
        provisioner = AnsibleProvisioner(
            './', host, guest, {'playbook': 'deploy.yml', 'vault_password_file': '.vpass'})
        provisioner.provision()
        assert re.match(
            'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --inventory-file /[/\w]+ '
            '--vault-password-file ./.vpass ./deploy.yml', mock_popen.call_args[0][0])

    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_ansible_playbooks_with_the_ask_vault_pass_option(self, mock_popen):
        host = Host(unittest.mock.Mock())
        guest = DebianGuest(unittest.mock.Mock())
        lxd_state = unittest.mock.Mock()
        lxd_state.network.__getitem__ = unittest.mock.MagicMock(
            return_value={'addresses': [{'family': 'init', 'address': '0.0.0.0', }, ]})
        guest.lxd_container.state.return_value = lxd_state
        provisioner = AnsibleProvisioner(
            './', host, guest, {'playbook': 'deploy.yml', 'ask_vault_pass': True})
        provisioner.provision()
        assert re.match(
            'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --inventory-file /[/\w]+ '
            '--ask-vault-pass ./deploy.yml', mock_popen.call_args[0][0])

    def test_can_properly_setup_ssh_for_alpine_guests(self):
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = Host(unittest.mock.Mock())
        guest = AlpineGuest(lxd_container)
        provisioner = AnsibleProvisioner('./', host, guest, {'playbook': 'deploy.yml'})
        provisioner.setup()
        assert lxd_container.execute.call_count == 4
        assert lxd_container.execute.call_args_list[0][0] == (['apk', 'update'], )
        assert lxd_container.execute.call_args_list[1][0] == \
            (['apk', 'add'] + AnsibleProvisioner.guest_required_packages_alpine, )
        assert lxd_container.execute.call_args_list[2][0] == (['rc-update', 'add', 'sshd'], )
        assert lxd_container.execute.call_args_list[3][0] == (['/etc/init.d/sshd', 'start'], )
