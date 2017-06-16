import unittest.mock

from lxdock.guests import DebianGuest


class TestDebianGuest:
    def test_can_install_packages(self):
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        guest = DebianGuest(lxd_container)
        guest.install_packages(['python', 'openssh', ])
        assert lxd_container.execute.call_count == 2
        assert lxd_container.execute.call_args_list[0][0] == \
            (['apt-get', 'update', ], )
        assert lxd_container.execute.call_args_list[1][0] == \
            (['apt-get', 'install', '-y', 'python', 'openssh', ], )
