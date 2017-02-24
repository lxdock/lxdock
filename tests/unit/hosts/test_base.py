import os
import platform
import unittest.mock
from pathlib import Path

import pytest

from lxdock.hosts import Host
from lxdock.hosts.base import InvalidHost


class TestGuest:
    def test_subclasses_cannot_be_registered_if_they_do_not_provide_a_guest_name(self):
        with pytest.raises(InvalidHost):
            class InvalidDummyHost(Host):
                name = None

    def test_can_detect_os_or_distribution(self):
        class DummyHost(Host):
            name = 'dummy'

        class PlatformHost(Host):
            name = platform.platform()

        assert not DummyHost.detect()
        assert PlatformHost.detect()

    @unittest.mock.patch.object(Path, 'open')
    def test_can_return_ssh_pubkey(self, mock_open):
        lxd_container = unittest.mock.Mock()
        host = Host(lxd_container)
        assert host.get_ssh_pubkey()
        assert mock_open.call_count == 1

    @unittest.mock.patch('subprocess.Popen')
    def test_can_give_current_user_access_to_share(self, mocked_call):
        lxd_container = unittest.mock.Mock()
        host = Host(lxd_container)
        host.give_current_user_access_to_share('.')
        assert mocked_call.call_count == 1
        assert mocked_call.call_args[0][0] == 'setfacl -Rdm u:{}:rwX .'.format(os.getuid())

    @unittest.mock.patch('subprocess.Popen')
    @unittest.mock.patch('os.stat')
    def test_can_give_mapped_user_access_to_share(self, mocked_stat, mocked_call):
        class MockedContainer(object):
            name = 'test'
        mocked_stat.return_value = unittest.mock.MagicMock(st_uid='19958953')
        lxd_container = MockedContainer()
        host = Host(lxd_container)
        host.give_mapped_user_access_to_share('.', '.')
        assert mocked_call.call_count == 1
        assert mocked_call.call_args[0] == (
            'setfacl -Rm user:lxd:rwx,default:user:lxd:rwx,user:19958953:rwx,default:user:19958953'
            ':rwx .',)
