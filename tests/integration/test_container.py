import os
import types
import unittest.mock

import pytest
from pylxd.exceptions import NotFound

from lxdock import constants
from lxdock.container import Container, must_be_created_and_running
from lxdock.exceptions import ContainerOperationFailed
from lxdock.test.testcases import LXDTestCase


THIS_DIR = os.path.join(os.path.dirname(__file__))


def test_must_be_created_and_running_decorator_works(persistent_container):
    @must_be_created_and_running
    def dummy_action(self):
        return 42
    persistent_container.dummy_action = types.MethodType(dummy_action, persistent_container)
    persistent_container.halt()
    assert persistent_container.dummy_action() is None
    persistent_container.up()
    assert persistent_container.dummy_action() == 42
    del persistent_container.dummy_action

    non_created_container_options = {
        'name': 'lxdock-nonexistingcontainer', 'image': 'ubuntu/xenial', 'mode': 'pull', }
    non_created_container = Container(
        'myproject', THIS_DIR, persistent_container.client, **non_created_container_options)
    non_created_container.dummy_action = types.MethodType(dummy_action, non_created_container)
    assert non_created_container.dummy_action() is None


class TestContainer(LXDTestCase):
    def test_can_set_up_a_container_that_does_not_exist(self):
        container_options = {
            'name': self.containername('newcontainer'), 'image': 'ubuntu/xenial', 'mode': 'pull', }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        assert container._container.status_code == constants.CONTAINER_RUNNING
        assert container._container.config['user.lxdock.made'] == '1'
        assert container._container.config['user.lxdock.homedir'] == THIS_DIR

    def test_can_set_up_a_container_that_is_already_up_and_running(self, persistent_container):
        persistent_container.up()
        assert persistent_container._container.status_code == constants.CONTAINER_RUNNING

    def test_can_set_up_a_container_that_exists_but_is_not_running(self, persistent_container):
        persistent_container.halt()
        assert persistent_container._container.status_code == constants.CONTAINER_STOPPED
        persistent_container.up()
        assert persistent_container._container.status_code == constants.CONTAINER_RUNNING

    def test_can_destroy_a_container_and_run_this_action_for_a_container_that_does_not_exist(self):
        container_options = {
            'name': self.containername('doesnotexist'), 'image': 'ubuntu/xenial', 'mode': 'pull', }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.destroy()
        assert not container.exists
        container.up()
        assert container.exists
        container.destroy()
        assert not container.exists

    def test_can_halt_a_container_that_is_running(self, persistent_container):
        persistent_container.halt()
        assert persistent_container._container.status_code == constants.CONTAINER_STOPPED

    def test_can_try_to_halt_a_container_that_is_already_stopped(self, persistent_container):
        persistent_container.halt()
        persistent_container.halt()
        assert persistent_container._container.status_code == constants.CONTAINER_STOPPED

    def test_can_provision_a_container_ansible(self):
        container_options = {
            'name': self.containername('willprovision'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'provisioning': [
                {'type': 'ansible',
                 'playbook': os.path.join(THIS_DIR, 'fixtures/provision_with_ansible.yml'), }
            ],
        }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        container.provision()
        assert container._container.files.get('/dummytest').strip() == b'dummytest'

    def test_can_provision_a_container_shell_inline(self):
        container_options = {
            'name': self.containername('willprovision'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'environment': {'PATH': '/dummy_test:/bin:/usr/bin:/usr/local/bin'},
            'provisioning': [
                {'type': 'shell',
                 'inline': """touch f && echo "Here's the PATH" $PATH >> /tmp/test.txt""", }
            ],
        }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        container.provision()
        assert container._container.files.get('/tmp/test.txt').strip() == (
            b"Here's the PATH /dummy_test:/bin:/usr/bin:/usr/local/bin")

    @unittest.mock.patch('subprocess.call')
    def test_can_open_a_shell_for_the_root_user(self, mocked_call, persistent_container):
        persistent_container.shell()
        assert mocked_call.call_count == 1
        assert mocked_call.call_args[0][0] == \
            'lxc exec {} -- su -m root'.format(persistent_container.lxd_name)

    @unittest.mock.patch('subprocess.call')
    def test_can_open_a_shell_for_a_specific_shelluser(self, mocked_call):
        container_options = {
            'name': self.containername('shellspecificuser'), 'image': 'ubuntu/xenial',
            'shell': {'user': 'test', 'home': '/opt', },
        }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        container.shell()
        assert mocked_call.call_count == 1
        assert mocked_call.call_args[0][0] == \
            'lxc exec {} --env HOME=/opt -- su -m test'.format(container.lxd_name)

    @unittest.mock.patch('subprocess.call')
    def test_can_run_quoted_shell_command_for_the_root_user(
            self, mocked_call, persistent_container):
        persistent_container.shell(cmd_args=['echo', 'he re"s', '-u', '$PATH'])
        assert mocked_call.call_count == 1
        assert mocked_call.call_args[0][0] == \
            'lxc exec {} -- su -m root -s {}'.format(
                persistent_container.lxd_name, persistent_container._guest_shell_script_file)
        script = persistent_container._container.files.get(
            persistent_container._guest_shell_script_file)
        assert script == b"""#!/bin/sh\necho 'he re"s' -u '$PATH'\n"""

    @unittest.mock.patch('subprocess.call')
    def test_can_run_quoted_shell_command_for_a_specific_shelluser(self, mocked_call):
        container_options = {
            'name': self.containername('shellspecificuser'), 'image': 'ubuntu/xenial',
            'shell': {'user': 'test', 'home': '/opt', },
        }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        container.shell(cmd_args=['echo', 'he re"s', '-u', '$PATH'])
        assert mocked_call.call_count == 1
        assert mocked_call.call_args[0][0] == \
            'lxc exec {} --env HOME=/opt -- su -m test -s {}'.format(
                container.lxd_name, container._guest_shell_script_file)
        script = container._container.files.get(container._guest_shell_script_file)
        assert script == b"""#!/bin/sh\necho 'he re"s' -u '$PATH'\n"""

    @unittest.mock.patch('subprocess.call')
    def test_can_set_shell_environment_variables(self, mocked_call):
        # Environment variables in the shell can be set through configuration.
        container_options = {
            'name': self.containername('shell-env'), 'image': 'ubuntu/xenial',
            'environment': {'FOO': 'bar', 'BAR': 42},
        }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        container.shell()
        assert container._container.config['environment.FOO'] == 'bar'
        assert container._container.config['environment.BAR'] == '42'

    def test_can_tell_if_a_container_exists_or_not(self, persistent_container):
        unknown_container = Container('myproject', THIS_DIR, self.client, **{
            'name': self.containername('unknown'), 'image': 'ubuntu/xenial', 'mode': 'pull', })
        assert persistent_container.exists
        assert not unknown_container.exists

    def test_can_tell_if_a_container_is_privileged_or_not(self, persistent_container):
        persistent_container._container.config['security.privileged'] = 'true'
        persistent_container._container.save(wait=True)
        assert persistent_container.is_privileged
        persistent_container._container.config['security.privileged'] = 'false'
        persistent_container._container.save(wait=True)
        assert not persistent_container.is_privileged

    def test_can_tell_if_a_container_is_provisioned_or_not(self, persistent_container):
        persistent_container._container.config['user.lxdock.provisioned'] = 'false'
        persistent_container._container.save(wait=True)
        assert not persistent_container.is_provisioned
        persistent_container._container.config['user.lxdock.provisioned'] = 'true'
        persistent_container._container.save(wait=True)
        assert persistent_container.is_provisioned

    def test_can_tell_if_a_container_is_running_or_not(self, persistent_container):
        persistent_container.halt()
        assert not persistent_container.is_running
        persistent_container.up()
        assert persistent_container.is_running

    def test_can_tell_if_a_container_is_stopped_or_not(self, persistent_container):
        persistent_container.halt()
        assert persistent_container.is_stopped
        persistent_container.up()
        assert not persistent_container.is_stopped

    def test_can_return_its_status(self, persistent_container):
        unknown_container = Container('myproject', THIS_DIR, self.client, **{
            'name': self.containername('unknown'), 'image': 'ubuntu/xenial', 'mode': 'pull', })
        assert unknown_container.status == 'not-created'
        persistent_container.halt()
        assert persistent_container.status == 'stopped'
        persistent_container.up()
        assert persistent_container.status == 'running'

    def test_create_users(self):
        password = '$6$cGzZBkDjOhGW$6C9wwqQteFEY4lQ6ZJBggE568SLSS7bIMKexwOD' \
                   '39mJQrJcZ5vIKJVIfwsKOZajhbPw0.Zqd0jU2NDLAnp9J/1'
        container_options = {
            'name': self.containername('createusers'), 'image': 'ubuntu/xenial',
            'users': [
                {'name': 'user01'},
                {'name': 'user02', 'home': '/opt/user02'},
                {'name': 'user03', 'password': password},
            ],
        }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        guest_mock = unittest.mock.Mock()
        container._container_guest = guest_mock
        container.up()
        assert guest_mock.create_user.call_count == 3
        assert guest_mock.create_user.call_args_list[0][0][0] == 'user01'
        assert guest_mock.create_user.call_args_list[1][0][0] == 'user02'
        assert guest_mock.create_user.call_args_list[2][0][0] == 'user03'
        assert guest_mock.create_user.call_args_list[1][1]['home'] == '/opt/user02'
        assert guest_mock.create_user.call_args_list[2][1]['password'] == password

    def test_get_container_lxc_config(self):
        """Test that _get_container generates a valid lxc_config
        """

        # The options below has an lxc_config value, that overrides some values
        # that are driven within lxdoc, these values are marked as invalid and should not
        # be passed directly to the container at creation time.
        container_options = {
            'name': self.containername('lxc-config'),
            'image': 'ubuntu/xenial',
            'lxc_config': {
                'security.privileged': 'invalid',
                'user.lxdock.homedir': 'invalid',
                'user.lxdock.made': 'invalid',
                'valid_key': 'valid_value',
            },
        }

        cont_return = ()  # mock container object to return

        def mock_create(container_config, *args, **kwargs):
            """Mocks the container create call, returns the mock container object
            and also ensures that the container_config is correct
            """
            config = container_config['config']
            # Values below should not be driven by the values in container_options
            assert config['security.privileged'] != 'invalid'
            assert config['user.lxdock.homedir'] != 'invalid'
            assert config['user.lxdock.made'] != 'invalid'
            # Value below is a custom value that should be passed from container_options
            assert config['valid_key'] == 'valid_value'
            return cont_return

        client_mock = unittest.mock.Mock(**{
            'containers.create.side_effect': mock_create,
            'containers.get.side_effect': NotFound(''),
        })

        container = Container('myproject', THIS_DIR, client_mock, **container_options)

        assert container._get_container() is cont_return
        assert client_mock.containers.get.called
        assert client_mock.containers.create.called

    def test_can_set_profiles(self):
        container_options = {
            'name': self.containername('newcontainer'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'profiles': ['default']}
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        assert container._container.status_code == constants.CONTAINER_RUNNING
        assert container._container.profiles == ['default']

    def test_raises_an_error_if_profile_does_not_exist(self):
        container_options = {
            'name': self.containername('newcontainer'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'profiles': ['default', '39mJQrJcZ5vIKJVIfwsKOZajhbPw0']}
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        with pytest.raises(ContainerOperationFailed):
            container.up()
