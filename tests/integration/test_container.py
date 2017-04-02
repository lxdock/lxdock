import os
import types
import unittest.mock

from lxdock import constants
from lxdock.container import Container, must_be_running
from lxdock.test.testcases import LXDTestCase


THIS_DIR = os.path.join(os.path.dirname(__file__))


def test_must_be_running_decorator_works(persistent_container):
    @must_be_running
    def dummy_action(self):
        return 42
    persistent_container.dummy_action = types.MethodType(dummy_action, persistent_container)
    persistent_container.halt()
    assert persistent_container.dummy_action() is None
    persistent_container.up()
    assert persistent_container.dummy_action() == 42
    del persistent_container.dummy_action


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

    def test_can_try_to_halt_a_container_that_is_already_stoppeds(self, persistent_container):
        persistent_container.halt()
        persistent_container.halt()
        assert persistent_container._container.status_code == constants.CONTAINER_STOPPED

    def test_can_provision_a_container(self):
        container_options = {
            'name': self.containername('willprovision'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'provisioning': [
                {'type': 'ansible',
                 'playbook': os.path.join(THIS_DIR, 'fixtures/provision_with_ansible.yml'), }
            ],
        }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        assert container._container.config['user.lxdock.provisioned'] == 'true'
        assert container._container.files.get('/dummytest').strip() == b'dummytest'

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
        persistent_container.provision()
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
