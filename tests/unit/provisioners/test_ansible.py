import unittest.mock

from lxdock.provisioners import AnsibleProvisioner


class TestAnsibleProvisioner:
    @unittest.mock.patch('subprocess.Popen')
    @unittest.mock.patch('tempfile.NamedTemporaryFile')
    def test_can_run_ansible_playbooks(self, mock_tempfile, mock_popen):
        class MockedTMPFile:
            name = 'tmpfile'

            def flush(self):
                pass

            def write(self, data):
                pass

        mock_tempfile.return_value.__enter__.return_value = MockedTMPFile()
        lxd_container = unittest.mock.Mock()
        lxd_state = unittest.mock.Mock()
        lxd_state.network.__getitem__ = unittest.mock.MagicMock(
            return_value={'addresses': [{'family': 'init', 'address': '0.0.0.0', }, ]})
        lxd_container.state.return_value = lxd_state
        provisioner = AnsibleProvisioner('./', lxd_container, {'playbook': 'deploy.yml'})
        provisioner.provision()
        assert mock_popen.call_args[0] == (
            'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --inventory-file '
            'tmpfile ./deploy.yml', )

    @unittest.mock.patch('subprocess.Popen')
    @unittest.mock.patch('tempfile.NamedTemporaryFile')
    def test_can_run_ansible_playbooks_with_the_vault_password_file_option(
            self, mock_tempfile, mock_popen):
        class MockedTMPFile:
            name = 'tmpfile'

            def flush(self):
                pass

            def write(self, data):
                pass

        mock_tempfile.return_value.__enter__.return_value = MockedTMPFile()
        lxd_container = unittest.mock.Mock()
        lxd_state = unittest.mock.Mock()
        lxd_state.network.__getitem__ = unittest.mock.MagicMock(
            return_value={'addresses': [{'family': 'init', 'address': '0.0.0.0', }, ]})
        lxd_container.state.return_value = lxd_state
        provisioner = AnsibleProvisioner(
            './', lxd_container, {'playbook': 'deploy.yml', 'vault_password_file': '.vpass'})
        provisioner.provision()
        assert mock_popen.call_args[0] == (
            'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --inventory-file '
            'tmpfile --vault-password-file ./.vpass ./deploy.yml', )

    @unittest.mock.patch('subprocess.Popen')
    @unittest.mock.patch('tempfile.NamedTemporaryFile')
    def test_can_run_ansible_playbooks_with_the_ask_vault_pass_option(
            self, mock_tempfile, mock_popen):
        class MockedTMPFile:
            name = 'tmpfile'

            def flush(self):
                pass

            def write(self, data):
                pass

        mock_tempfile.return_value.__enter__.return_value = MockedTMPFile()
        lxd_container = unittest.mock.Mock()
        lxd_state = unittest.mock.Mock()
        lxd_state.network.__getitem__ = unittest.mock.MagicMock(
            return_value={'addresses': [{'family': 'init', 'address': '0.0.0.0', }, ]})
        lxd_container.state.return_value = lxd_state
        provisioner = AnsibleProvisioner(
            './', lxd_container, {'playbook': 'deploy.yml', 'ask_vault_pass': True})
        provisioner.provision()
        assert mock_popen.call_args[0] == (
            'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --inventory-file '
            'tmpfile --ask-vault-pass ./deploy.yml', )
