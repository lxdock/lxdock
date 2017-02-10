import os

from nomad import constants
from nomad.container import Container
from nomad.test.testcases import LXDTestCase


THIS_DIR = os.path.join(os.path.dirname(__file__))


class TestContainer(LXDTestCase):
    def test_can_set_up_a_container_that_does_not_exist(self):
        container_options = {
            'name': self.containername('dummy'), 'image': 'ubuntu/xenial', 'mode': 'pull', }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        container.up()
        assert container._container.status_code == constants.CONTAINER_RUNNING
        assert container._container.config['user.nomad.made'] == '1'
        assert container._container.config['user.nomad.homedir'] == THIS_DIR

    def test_can_set_up_a_container_that_is_already_up_and_running(self, persistent_container):
        persistent_container.up()
        assert persistent_container._container.status_code == constants.CONTAINER_RUNNING

    def test_can_set_up_a_container_that_exists_but_is_not_running(self, persistent_container):
        persistent_container.halt()
        assert persistent_container._container.status_code == constants.CONTAINER_STOPPED
        persistent_container.up()
        assert persistent_container._container.status_code == constants.CONTAINER_RUNNING

    def test_can_tell_if_a_container_exists_or_not(self, persistent_container):
        unkonwn_container = Container('myproject', THIS_DIR, self.client, **{
            'name': self.containername('unkonwn'), 'image': 'ubuntu/xenial', 'mode': 'pull', })
        assert persistent_container.exists
        assert not unkonwn_container.exists

    def test_can_tell_if_a_container_is_privileged_or_not(self, persistent_container):
        persistent_container._container.config['security.privileged'] = 'true'
        persistent_container._container.save(wait=True)
        assert persistent_container.is_privileged
        persistent_container._container.config['security.privileged'] = 'false'
        persistent_container._container.save(wait=True)
        assert not persistent_container.is_privileged

    def test_can_tell_if_a_container_is_provisioned_or_not(self, persistent_container):
        persistent_container._container.config['user.nomad.provisioned'] = 'false'
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
        unkonwn_container = Container('myproject', THIS_DIR, self.client, **{
            'name': self.containername('unkonwn'), 'image': 'ubuntu/xenial', 'mode': 'pull', })
        assert unkonwn_container.status == 'not-created'
        persistent_container.halt()
        assert persistent_container.status == 'stopped'
        persistent_container.up()
        assert persistent_container.status == 'running'
