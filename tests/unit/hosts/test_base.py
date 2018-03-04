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
        host = Host()
        assert host.get_ssh_pubkey()
        assert mock_open.call_count == 1

    @unittest.mock.patch("os.getuid")
    @unittest.mock.patch("os.getgid")
    def test_uidgid(self, mock_getuid, mock_getgid):
        mock_getuid.return_value = 10000
        mock_getgid.return_value = 10001

        host = Host()

        assert host.uidgid(), (10000, 10001)
