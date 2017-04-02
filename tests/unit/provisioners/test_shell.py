import unittest.mock

from lxdock.guests import DebianGuest
from lxdock.hosts import Host
from lxdock.provisioners import ShellProvisioner


class TestShellProvisioner:
    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_commands_on_the_host_side(self, mock_popen):
        host = Host(unittest.mock.Mock())
        guest = DebianGuest(unittest.mock.Mock())
        provisioner = ShellProvisioner(
            './', host, guest, {'inline': 'touch f', 'side': 'host', })
        provisioner.provision()
        assert mock_popen.call_args[0] == ('touch f', )

    def test_can_run_commands_on_the_guest_side(self):
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = Host(unittest.mock.Mock())
        guest = DebianGuest(lxd_container)
        provisioner = ShellProvisioner(
            './', host, guest, {'inline': 'echo TEST'})
        provisioner.provision()
        assert lxd_container.execute.call_count == 1
        assert lxd_container.execute.call_args_list[0][0] == (['echo', 'TEST'], )

    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_a_script_on_the_host_side(self, mock_popen):
        host = Host(unittest.mock.Mock())
        guest = DebianGuest(unittest.mock.Mock())
        provisioner = ShellProvisioner(
            './', host, guest, {'script': 'test.sh', 'side': 'host', })
        provisioner.provision()
        assert mock_popen.call_args[0] == ('./test.sh', )

    @unittest.mock.patch('builtins.open')
    def test_can_run_a_script_on_the_guest_side(self, mock_open):
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = Host(unittest.mock.Mock())
        guest = DebianGuest(lxd_container)
        provisioner = ShellProvisioner(
            './', host, guest, {'script': 'test.sh', })
        provisioner.provision()
        assert lxd_container.execute.call_count == 2
        assert lxd_container.execute.call_args_list[0][0] == (['chmod', '+x', '/tmp/test.sh', ], )
        assert lxd_container.execute.call_args_list[1][0] == (['/tmp/test.sh', ], )
