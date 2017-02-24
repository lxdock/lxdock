import pytest

from lxdock.provisioners import Provisioner
from lxdock.provisioners.base import InvalidProvisioner


class TestProvisioner:
    def test_subclasses_cannot_be_registered_if_they_do_not_provide_a_provisioner_name(self):
        with pytest.raises(InvalidProvisioner):
            class InvalidDummyHost(Provisioner):
                name = None
