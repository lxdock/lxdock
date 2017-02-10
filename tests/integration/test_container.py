import os

from nomad import constants
from nomad.container import Container
from nomad.test.testcases import LXDTestCase


THIS_DIR = os.path.join(os.path.dirname(__file__))


class TestContainer(LXDTestCase):
    def test_can_set_up_containers(self):
        # Setup
        container_options = {
            'name': self.containername('dummy'), 'image': 'ubuntu/xenial', 'mode': 'pull', }
        container = Container('myproject', THIS_DIR, self.client, **container_options)
        # Run & check that we can set up the container that does not exist
        container.up()
        assert container._container.status_code == constants.CONTAINER_RUNNING
        assert container._container.config['user.nomad.made'] == '1'
        assert container._container.config['user.nomad.homedir'] == THIS_DIR
        # Run & check that we can set up the container event if it already exists
        container.up()
        assert container._container.status_code == constants.CONTAINER_RUNNING
        # Run & check that we can set up the container event if it was halted
        container.halt()
        assert container._container.status_code == constants.CONTAINER_STOPPED
        container.up()
        assert container._container.status_code == constants.CONTAINER_RUNNING
