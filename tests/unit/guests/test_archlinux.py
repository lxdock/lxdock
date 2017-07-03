from lxdock.guests import ArchLinuxGuest
from lxdock.test import FakeContainer


class TestArchLinuxGuest:
    def test_can_install_packages(self):
        guest = ArchLinuxGuest(FakeContainer())
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['pacman', '-S', '--noconfirm', 'python', 'openssh'], )
