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
        provisioner = AnsibleProvisioner(lxd_container, {'playbook': 'deploy.yml'})
        provisioner.provision()
        assert mock_popen.call_args[0] == (
            'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i tmpfile deploy.yml', )
