import unittest.mock

import pytest

from lxdock.guests import DebianGuest
from lxdock.provisioners import Provisioner
from lxdock.provisioners.base import InvalidProvisioner
from lxdock.test import FakeContainer


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

        container = FakeContainer()
        lxd_container = container._container
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = unittest.mock.Mock()
        guest = DebianGuest(container)
        provisioner = DummyProvisioner('./', host, [guest], {})
        provisioner.setup()
        assert lxd_container.execute.call_count == 2
        assert lxd_container.execute.call_args_list[0][0] == \
            (['apt-get', 'update'], )
        assert lxd_container.execute.call_args_list[1][0] == \
            (['apt-get', 'install', '-y', 'test01', 'test02', ], )

    def test_trigger_specific_setup_on_the_guest_if_the_related_method_is_defined(self):
        class DummyProvisioner(Provisioner):
            name = 'myprovisioner'
            schema = {'test': 'test', }
            called = False

            def setup_guest_debian(self, guest):
                self.called = True

        container = FakeContainer()
        lxd_container = container._container
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = unittest.mock.Mock()
        guest = DebianGuest(container)
        provisioner = DummyProvisioner('./', host, [guest], {})
        provisioner.setup()
        assert provisioner.called
