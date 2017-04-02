import unittest.mock

from lxdock.guests import GentooGuest


class TestGentooGuest:
    def test_should_install_packages_if_not_installed(self):
        lxd_container = unittest.mock.Mock()
        # Retcode 1: "No installed packages matching {keyword}"
        lxd_container.execute.return_value = (1, 'ok', '')
        guest = GentooGuest(lxd_container)
        guest.install_packages(['python', 'openssh', ])
        assert lxd_container.execute.call_count == 5
        assert lxd_container.execute.call_args_list[0][0] == \
            (['emerge', 'app-portage/gentoolkit'], )
        for i, p in enumerate(['python', 'openssh', ]):
            assert lxd_container.execute.call_args_list[2 * i + 1][0] == (['equery', 'list', p], )
            assert lxd_container.execute.call_args_list[2 * i + 2][0] == (['emerge', p], )

    def test_should_not_reinstall_packages_if_already_installed(self):
        lxd_container = unittest.mock.Mock()
        # Retcode 0: the package has been found locally
        lxd_container.execute.return_value = (0, 'ok', '')
        guest = GentooGuest(lxd_container)
        guest.install_packages(['python', 'openssh', ])
        assert lxd_container.execute.call_count == 3
        assert lxd_container.execute.call_args_list[0][0] == \
            (['emerge', 'app-portage/gentoolkit'], )
        for i, p in enumerate(['python', 'openssh', ]):
            assert lxd_container.execute.call_args_list[i + 1][0] == (['equery', 'list', p], )
