from lxdock.guests import GentooGuest
from lxdock.test import FakeContainer


class TestGentooGuest:
    def test_should_install_packages_if_not_installed(self):
        guest = GentooGuest(FakeContainer())
        # Retcode 1: "No installed packages matching {keyword}"
        guest.lxd_container.execute.return_value = (1, 'ok', '')
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 5
        assert guest.lxd_container.execute.call_args_list[0][0] == \
            (['emerge', 'app-portage/gentoolkit'], )
        for i, p in enumerate(['python', 'openssh', ]):
            assert guest.lxd_container.execute.call_args_list[2 * i + 1][0] == \
                (['equery', 'list', p], )
            assert guest.lxd_container.execute.call_args_list[2 * i + 2][0] == (['emerge', p], )

    def test_should_not_reinstall_packages_if_already_installed(self):
        guest = GentooGuest(FakeContainer())
        # Retcode 0: the package has been found locally
        guest.lxd_container.execute.return_value = (0, 'ok', '')
        guest.install_packages(['python', 'openssh', ])
        assert guest.lxd_container.execute.call_count == 3
        assert guest.lxd_container.execute.call_args_list[0][0] == \
            (['emerge', 'app-portage/gentoolkit'], )
        for i, p in enumerate(['python', 'openssh', ]):
            assert guest.lxd_container.execute.call_args_list[i + 1][0] == (['equery', 'list', p], )
