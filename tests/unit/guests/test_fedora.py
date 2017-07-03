from lxdock.guests import FedoraGuest
from lxdock.test import FakeContainer


class TestFedoraGuest:
    def test_can_install_packages(self):
        guest = FedoraGuest(FakeContainer())
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['dnf', '-y', 'install', 'python', 'openssh', ], )
