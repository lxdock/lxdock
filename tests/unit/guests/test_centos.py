from lxdock.guests import CentosGuest
from lxdock.test import FakeContainer


class TestCentosGuest:
    def test_can_install_packages(self):
        guest = CentosGuest(FakeContainer())
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['yum', '-y', 'install', 'python', 'openssh', ], )
