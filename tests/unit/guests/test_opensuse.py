from lxdock.guests import OpenSUSEGuest
from lxdock.test import FakeContainer


class TestOpenSUSEGuest:
    def test_can_install_packages(self):
        guest = OpenSUSEGuest(FakeContainer())
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['zypper', '--non-interactive', 'install', 'python', 'openssh', ], )
