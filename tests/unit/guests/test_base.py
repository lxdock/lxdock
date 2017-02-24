import unittest.mock

import pytest
from pylxd.exceptions import NotFound

from lxdock.guests import Guest
from lxdock.guests.base import InvalidGuest


class TestGuest:
    def test_subclasses_cannot_be_registered_if_they_do_not_provide_a_guest_name(self):
        with pytest.raises(InvalidGuest):
            class InvalidDummyGuest(Guest):
                name = None

    def test_can_detect_os_or_distribution(self):
        class DummyGuest(Guest):
            name = 'dummy'
        lxd_container_1 = unittest.mock.Mock()
        lxd_container_1.files.get.return_value = 'ID=dummy'
        lxd_container_2 = unittest.mock.Mock()
        lxd_container_2.files.get.return_value = 'ID=unknown'
        lxd_container_3 = unittest.mock.Mock()
        lxd_container_3.files.get.side_effect = NotFound(response=unittest.mock.Mock())
        assert DummyGuest.detect(lxd_container_1)
        assert not DummyGuest.detect(lxd_container_2)
        assert not DummyGuest.detect(lxd_container_3)

    def test_can_add_ssh_pubkey_to_root_authorized_keys(self):
        class DummyGuest(Guest):
            name = 'dummy'
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        guest = DummyGuest(lxd_container)
        guest.add_ssh_pubkey_to_root_authorized_keys('pubkey')
        assert lxd_container.execute.call_count == 1
        assert lxd_container.execute.call_args[0] == (['mkdir', '-p', '/root/.ssh'], )
        assert lxd_container.files.put.call_count == 1
        assert lxd_container.files.put.call_args[0] == ('/root/.ssh/authorized_keys', 'pubkey', )

    def test_can_create_a_user_with_a_default_home_directory(self):
        class DummyGuest(Guest):
            name = 'dummy'
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        guest = DummyGuest(lxd_container)
        guest.create_user('usertest')
        assert lxd_container.execute.call_count == 1
        assert lxd_container.execute.call_args[0] == (['useradd', '--create-home', 'usertest'], )

    def test_can_create_a_user_with_a_custom_home_directory(self):
        class DummyGuest(Guest):
            name = 'dummy'
        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        guest = DummyGuest(lxd_container)
        guest.create_user('usertest', '/opt/usertest')
        assert lxd_container.execute.call_count == 1
        assert lxd_container.execute.call_args[0] == \
            (['useradd', '--create-home', '--home-dir', '/opt/usertest', 'usertest'], )
