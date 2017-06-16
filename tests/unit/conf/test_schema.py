import unittest.mock

import pytest
from voluptuous import All, Any, Boolean, Coerce, Length
from voluptuous.error import Invalid

from lxdock.conf.schema import get_schema


class MockProvisioner1(object):
    name = 'mp1'
    schema = {'a': str, 'b': Coerce(int)}


class MockProvisioner2(object):
    name = 'mp2'
    schema = All({'a': str}, {'a': Length(min=5, max=5)})


class MockProvisioner3(object):
    name = 'mp3'
    schema = Any({'a': str}, {'b': Boolean()})


class TestValidateProvisionerSchemas:
    @unittest.mock.patch('lxdock.conf.schema.Provisioner')
    def test_can_validate_and_coerce_multiple_provisioner_schemas(self, mock_Provisioner):
        mock_Provisioner.provisioners = {
            'mp1': MockProvisioner1,
            'mp2': MockProvisioner2,
            'mp3': MockProvisioner3}
        schema = get_schema()
        validated = schema({
            'name': 'dummy-test',
            'provisioning': [{
                'type': 'mp1',
                'a': 'dummy',
                'b': '16'
            }, {
                'type': 'mp2',
                'a': 'dummy',
            }, {
                'type': 'mp3',
                'b': 'yes'
            }]
        })
        assert validated == {
            'name': 'dummy-test',
            'provisioning': [{
                'type': 'mp1',
                'a': 'dummy',
                'b': 16  # Check Coerce
            }, {
                'type': 'mp2',
                'a': 'dummy',
            }, {
                'type': 'mp3',
                'b': True  # Check Boolean
            }]
        }

    @unittest.mock.patch('lxdock.conf.schema.Provisioner')
    def test_raise_invalid_if_provisioner_schema_is_not_satisfied(self, mock_Provisioner):
        mock_Provisioner.provisioners = {
            'mp1': MockProvisioner1,
            'mp2': MockProvisioner2,
            'mp3': MockProvisioner3}
        schema = get_schema()
        with pytest.raises(Invalid) as e:
            schema({
                'name': 'dummy-test',
                'provisioning': [{
                    'type': 'mp1',
                    'a': 'dummy',
                    'b': '16'
                }, {
                    'type': 'mp2',
                    'a': 'dummydummy',  # Exceeds Length(min=5, max=5)
                }, {
                    'type': 'mp3',
                    'b': 'yes'
                }]
            })
        assert "['provisioning'][1]['a']" in str(e)
