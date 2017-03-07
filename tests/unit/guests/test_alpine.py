import unittest.mock

from lxdock.guests import AlpineGuest


class TestAlpineGuest:
    def test_can_install_barebones_packages(self):
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        guest = AlpineGuest(lxd_container)
        guest.install_barebones_packages()
        assert lxd_container.execute.call_count == 4
        assert lxd_container.execute.call_args_list[0][0] == (['apk', 'update'], )
        assert lxd_container.execute.call_args_list[1][0] == \
            (['apk', 'add'] + AlpineGuest.barebones_packages, )
        assert lxd_container.execute.call_args_list[2][0] == \
            (['rc-update', 'add', 'sshd'], )
        assert lxd_container.execute.call_args_list[3][0] == \
            (['/etc/init.d/sshd', 'start'], )
