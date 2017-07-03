import unittest.mock

from lxdock.guests import DebianGuest
from lxdock.hosts import Host
from lxdock.provisioners import ShellProvisioner
from lxdock.test import FakeContainer


class TestShellProvisioner:
    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_commands_on_the_host_side(self, mock_popen):
        host = Host()
        guest = DebianGuest(FakeContainer())
        provisioner = ShellProvisioner(
            './', host, [guest], {
                'inline': """touch f && echo "Here's the PATH" $PATH >> /tmp/test.txt""",
                'side': 'host', })
        provisioner.provision()
        assert mock_popen.call_args[0] == (
            """sh -c 'touch f && echo "Here'"'"'s the PATH" $PATH >> /tmp/test.txt'""", )

    def test_can_run_commands_on_the_guest_side(self):
        container = FakeContainer()
        lxd_container = container._container
        host = Host()
        guest = DebianGuest(container)
        cmd = """touch f && echo "Here's the PATH" $PATH >> /tmp/test.txt"""
        provisioner = ShellProvisioner(
            './', host, [guest], {'inline': cmd})
        provisioner.provision()
        assert lxd_container.execute.call_count == 1
        assert lxd_container.execute.call_args_list[0][0] == (['sh', '-c', cmd], )

    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_a_script_on_the_host_side(self, mock_popen):
        host = Host()
        guest = DebianGuest(unittest.mock.Mock())
        provisioner = ShellProvisioner(
            './', host, [guest], {'script': 'test.sh', 'side': 'host', })
        provisioner.provision()
        assert mock_popen.call_args[0] == ('./test.sh', )

    @unittest.mock.patch('builtins.open')
    def test_can_run_a_script_on_the_guest_side(self, mock_open):
        container = FakeContainer()
        lxd_container = container._container
        host = Host()
        guest = DebianGuest(container)
        provisioner = ShellProvisioner(
            './', host, [guest], {'script': 'test.sh', })
        provisioner.provision()
        assert lxd_container.execute.call_count == 2
        assert lxd_container.execute.call_args_list[0][0] == (['chmod', '+x', '/tmp/test.sh', ], )
        assert lxd_container.execute.call_args_list[1][0] == (['/tmp/test.sh', ], )
