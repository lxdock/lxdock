import os
import pathlib
import tempfile
import unittest.mock

import pytest
from pylxd.exceptions import NotFound

from lxdock.guests import Guest
from lxdock.guests.base import InvalidGuest
from lxdock.test import FakeContainer


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
        guest = DummyGuest(FakeContainer())
        guest.add_ssh_pubkey_to_root_authorized_keys('pubkey')
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == (['mkdir', '-p', '/root/.ssh'], )
        assert guest.lxd_container.files.put.call_count == 1
        assert guest.lxd_container.files.put.call_args[0] == \
            ('/root/.ssh/authorized_keys', 'pubkey', )

    def test_can_create_a_user_with_a_default_home_directory(self):
        class DummyGuest(Guest):
            name = 'dummy'
        guest = DummyGuest(FakeContainer())
        guest.create_user('usertest')
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['useradd', '--create-home', 'usertest'], )

    def test_can_create_a_user_with_a_custom_home_directory(self):
        class DummyGuest(Guest):
            name = 'dummy'
        guest = DummyGuest(FakeContainer())
        guest.create_user('usertest', home='/opt/usertest')
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['useradd', '--create-home', '--home-dir', '/opt/usertest', 'usertest'], )

    def test_can_create_a_user_with_a_custom_password(self):
        class DummyGuest(Guest):
            name = 'dummy'
        password = '$6$cGzZBkDjOhGW$6C9wwqQteFEY4lQ6ZJBggE568SLSS7bIMKexwOD' \
                   '39mJQrJcZ5vIKJVIfwsKOZajhbPw0.Zqd0jU2NDLAnp9J/1'
        guest = DummyGuest(FakeContainer())
        guest.create_user('usertest', password=password)
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == \
            (['useradd', '--create-home', '-p', password, 'usertest'], )

    def test_can_copy_file(self):
        class DummyGuest(Guest):
            name = 'dummy'
        guest = DummyGuest(FakeContainer())
        guest.lxd_container.files.put.return_value = True
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'dummy file')
            f.flush()
            guest.copy_file(pathlib.Path(f.name), pathlib.PurePath('/a/b/c'))
        assert guest.lxd_container.execute.call_count == 1
        assert guest.lxd_container.execute.call_args[0] == (['mkdir', '-p', '/a/b'], )
        assert guest.lxd_container.files.put.call_count == 1
        assert guest.lxd_container.files.put.call_args[0] == ('/a/b/c', b'dummy file')

    @unittest.mock.patch('tarfile.TarFile.add')
    @unittest.mock.patch('tarfile.TarFile.close')
    def test_can_copy_directory(self, mock_close, mock_add):
        class DummyGuest(Guest):
            name = 'dummy'
        guest = DummyGuest(FakeContainer())
        guest.lxd_container.files.put.return_value = True
        with tempfile.TemporaryDirectory() as d:
            os.mkdir('{}/d1'.format(d))
            os.mkdir('{}/d1/d2'.format(d))
            with open('{}/d1/f1'.format(d), 'wb') as f1:
                f1.write(b'dummy f1')
            with open('{}/d1/d2/f2'.format(d), 'wb') as f2:
                f2.write(b'dummy f2')
            with open('{}/f3'.format(d), 'wb') as f3:
                f3.write(b'dummy f3')
            guest.copy_directory(pathlib.Path(d), pathlib.PurePosixPath('/a/b/c'))

        assert mock_add.call_count == 1
        assert mock_add.call_args[0][0] == str(pathlib.Path(d))
        assert mock_add.call_args[1]['arcname'] == '.'

        assert mock_close.call_count == 1

        assert guest.lxd_container.execute.call_count == 4
        assert guest.lxd_container.execute.call_args_list[0][0] == (['mkdir', '-p', '/a/b/c'], )
        assert guest.lxd_container.execute.call_args_list[1][0] == ([
            'mkdir', '-p', str(pathlib.PurePosixPath(guest._guest_temporary_tar_path).parent)], )
        assert guest.lxd_container.execute.call_args_list[2][0] == ([
            'tar', '-xf', guest._guest_temporary_tar_path, '-C', '/a/b/c'], )
        assert guest.lxd_container.execute.call_args_list[3][0] == ([
            'rm', '-f', guest._guest_temporary_tar_path], )

        assert guest.lxd_container.files.put.call_count == 1
        assert guest.lxd_container.files.put.call_args[0][0] == guest._guest_temporary_tar_path
