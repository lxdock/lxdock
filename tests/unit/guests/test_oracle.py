from lxdock.guests import OracleLinuxGuest
from lxdock.test import FakeContainer


class TestOracleLinuxGuest:
    def test_can_install_packages(self):
        guest = OracleLinuxGuest(FakeContainer())
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['yum', '-y', 'install', 'python', 'openssh', ], )
