import unittest.mock

from lxdock.guests import DebianGuest


class TestDebianGuest:
    def test_can_install_packages(self):
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        guest = DebianGuest(lxd_container)
        guest.install_packages(['python', 'openssh', ])
        assert lxd_container.execute.call_count == 1
        assert lxd_container.execute.call_args[0] == \
            (['apt-get', 'install', '-y', 'python', 'openssh', ], )
