from lxdock.guests import AlpineGuest
from lxdock.test import FakeContainer


class TestAlpineGuest:
    def test_can_install_packages(self):
        guest = AlpineGuest(FakeContainer())
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 2
        assert guest.lxd_container.execute.call_args_list[0][0] == (['apk', 'update'], )
        assert guest.lxd_container.execute.call_args_list[1][0] == \
            (['apk', 'add', 'python', 'openssh'], )
