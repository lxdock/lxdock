"""
    LXDock specific testcases & test wrappers
    =========================================
    This module provides testcase classes that can be used to perform common operations before or
    after test execution.
"""

from .. import constants
from ..client import get_client

__all__ = ['LXDTestCase', ]


TEST_CONTAINER_INJECTED_ID = 'lxdock-pytest-'


def _remove_test_containers(client=None):
    """ This function can be used to ensure test containers are removed after test execution. """
    client = client or get_client()
    test_containers = list(filter(
        lambda c: TEST_CONTAINER_INJECTED_ID in c.name, client.containers.all()))
    [c.stop(wait=True) for c in test_containers if c.status_code == constants.CONTAINER_RUNNING]
    [c.delete() for c in test_containers]


class LXDTestCase:
    """ Base test class used to run integration tests that require the use of LXD. """

    @classmethod
    def teardown_class(cls):
        _remove_test_containers()

    def teardown_method(self, method):
        _remove_test_containers(client=self.client)

    ##################################
    # UTILITY METHODS AND PROPERTIES #
    ##################################

    def containername(self, name):
        """ Helper to construct a container name that should be deleted after each test. """
        return TEST_CONTAINER_INJECTED_ID + name

    @property
    def client(self):
        """ Returns a client instance to use when running tests requiring a LXD client. """
        if not hasattr(self, '_client'):
            self._client = get_client()
        return self._client
