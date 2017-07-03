from lxdock.guests import DebianGuest
from lxdock.test import FakeContainer


class TestDebianGuest:
    def test_can_install_packages(self):
        guest = DebianGuest(FakeContainer())
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 2
        assert guest.lxd_container.execute.call_args_list[0][0] == \
            (['apt-get', 'update', ], )
        assert guest.lxd_container.execute.call_args_list[1][0] == \
            (['apt-get', 'install', '-y', 'python', 'openssh', ], )
