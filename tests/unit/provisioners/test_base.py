import unittest.mock

import pytest

from lxdock.guests import DebianGuest
from lxdock.provisioners import Provisioner
from lxdock.provisioners.base import InvalidProvisioner


class TestProvisioner:
    def test_subclasses_cannot_be_registered_if_they_do_not_provide_a_provisioner_name(self):
        with pytest.raises(InvalidProvisioner):
            class InvalidDummyProvisioner(Provisioner):
                name = None
                schema = {}

    def test_subclasses_cannot_be_registered_if_they_do_not_provide_a_schema_dict(self):
        with pytest.raises(InvalidProvisioner):
            class InvalidDummyProvisioner(Provisioner):
                name = 'myprovisioner'
                schema = None

    def test_trigger_packages_installation_on_the_guest_if_the_related_attr_is_defined(self):
        class DummyProvisioner(Provisioner):
            name = 'myprovisioner'
            schema = {'test': 'test', }

            guest_required_packages_debian = ['test01', 'test02', ]

        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = unittest.mock.Mock()
        guest = DebianGuest(lxd_container)
        provisioner = DummyProvisioner('./', host, guest, {})
        provisioner.setup()
        assert lxd_container.execute.call_count == 1
        assert lxd_container.execute.call_args[0] == \
            (['apt-get', 'install', '-y', 'test01', 'test02', ], )

    def test_trigger_specific_setup_on_the_guest_if_the_related_method_is_defined(self):
        class DummyProvisioner(Provisioner):
            name = 'myprovisioner'
            schema = {'test': 'test', }
            called = False

            def setup_guest_debian(self):
                self.called = True

        lxd_container = unittest.mock.Mock()
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = unittest.mock.Mock()
        guest = DebianGuest(lxd_container)
        provisioner = DummyProvisioner('./', host, guest, {})
        provisioner.setup()
        assert provisioner.called
