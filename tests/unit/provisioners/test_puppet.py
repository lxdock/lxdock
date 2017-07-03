import os
import tempfile
import unittest.mock
from pathlib import Path, PurePosixPath

import pytest
from voluptuous import Schema
from voluptuous.error import Invalid

from lxdock.exceptions import ProvisionFailed
from lxdock.guests import Guest
from lxdock.hosts import Host
from lxdock.provisioners import PuppetProvisioner


class TestPuppetProvisionerSchema:
    def test_can_set_default_manifest_file(self):
        with tempfile.TemporaryDirectory() as d:
            with (Path(d) / 'default.pp').open('w') as f:
                f.write('dummy pp file')
            config = {'manifests_path': d}
            try:
                final_config = Schema(PuppetProvisioner.schema)(config)
            except Invalid as e:
                pytest.fail("schema validation didn't pass: {}".format(e))
            assert final_config == {
                'manifest_file': 'default.pp',
                'manifests_path': d}

    def test_can_set_default_environment(self):
        with tempfile.TemporaryDirectory() as d:
            os.mkdir(str(Path(d) / 'production'))
            config = {'environment_path': d}
            try:
                final_config = Schema(PuppetProvisioner.schema)(config)
            except Invalid as e:
                pytest.fail("schema validation didn't pass: {}".format(e))
            assert final_config == {
                'environment': 'production',
                'environment_path': d}

    @unittest.mock.patch('lxdock.provisioners.puppet.IsDir')
    @unittest.mock.patch('lxdock.provisioners.puppet.IsFile')
    def test_can_set_default_mode_and_manifest_file(self, mock_isfile, mock_isdir):
        config = {}
        try:
            final_config = Schema(PuppetProvisioner.schema)(config)
        except Invalid as e:
            pytest.fail("schema validation didn't pass: {}".format(e))
        assert final_config == {
            'manifests_path': 'manifests',
            'manifest_file': 'default.pp'}


class TestPuppetProvisioner:
    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_run_puppet_manifest_mode(self, mock_run, mock_copy_dir):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'test_site.pp',
            'manifests_path': 'test_manifests'})
        provisioner.provision()

        assert mock_copy_dir.call_count == 1
        assert mock_copy_dir.call_args_list[0][0][0] == Path('test_manifests')
        assert mock_copy_dir.call_args_list[0][0][1] == PurePosixPath(
            provisioner._guest_manifests_path)

        assert mock_run.call_count == 2
        assert mock_run.call_args_list[0][0][0] == ['which', 'puppet']
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            'puppet apply --detailed-exitcodes --manifestdir {} {}'.format(
                PurePosixPath(provisioner._guest_manifests_path),
                PurePosixPath(provisioner._guest_manifests_path) / 'test_site.pp')]

    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_run_puppet_environment_mode(self, mock_run, mock_copy_dir):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'environment': 'test_production',
            'environment_path': 'test_environments'})
        provisioner.provision()

        assert mock_copy_dir.call_count == 1
        assert mock_copy_dir.call_args_list[0][0][0] == Path('test_environments')
        assert mock_copy_dir.call_args_list[0][0][1] == PurePosixPath(
            provisioner._guest_environment_path)

        assert mock_run.call_count == 2
        assert mock_run.call_args_list[0][0][0] == ['which', 'puppet']
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            'puppet apply --detailed-exitcodes '
            '--environmentpath {} --environment {}'.format(
                PurePosixPath(provisioner._guest_environment_path),
                'test_production')]

    @unittest.mock.patch.object(Guest, 'copy_file')
    @unittest.mock.patch.object(Guest, 'run')
    def test_raise_error_if_puppet_is_not_found(self, mock_run, mock_copy_file):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 1  # Mock the error
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'test_site.pp',
            'manifests_path': 'test_manifests'})
        with pytest.raises(ProvisionFailed):
            provisioner.provision()
        assert mock_run.call_count == 1
        assert mock_run.call_args[0] == (['which', 'puppet'], )
        assert mock_copy_file.call_count == 0

    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_set_binary_path(self, mock_run, mock_copy_dir):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'test_site.pp',
            'manifests_path': 'test_manifests',
            'binary_path': '/test/path'})
        provisioner.provision()

        assert mock_run.call_count == 2
        assert mock_run.call_args_list[0][0][0] == ['test', '-x', '/test/path/puppet']
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            '/test/path/puppet apply --detailed-exitcodes --manifestdir {} {}'.format(
                PurePosixPath(provisioner._guest_manifests_path),
                PurePosixPath(provisioner._guest_manifests_path) / 'test_site.pp')]

    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_set_facter(self, mock_run, mock_copy_dir):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'site.pp',
            'manifests_path': 'test_manifests',
            'facter': {'foo': 'bah', 'bar': 'baz baz'}})
        provisioner.provision()
        assert mock_run.call_count == 2
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            "FACTER_bar='baz baz' FACTER_foo=bah "
            "puppet apply --detailed-exitcodes --manifestdir {} {}".format(
                PurePosixPath(provisioner._guest_manifests_path),
                PurePosixPath(provisioner._guest_manifests_path) / 'site.pp')]

    @unittest.mock.patch.object(Guest, 'copy_file')
    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_set_hiera_config_path(self, mock_run, mock_copy_dir, mock_copy_file):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'site.pp',
            'manifests_path': 'test_manifests',
            'hiera_config_path': 'hiera.yaml'})
        provisioner.provision()

        assert mock_copy_file.call_count == 1
        assert mock_copy_file.call_args_list[0][0][0] == Path('hiera.yaml')
        assert mock_copy_file.call_args_list[0][0][1] == PurePosixPath(
            provisioner._guest_hiera_file)

        assert mock_run.call_count == 2
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            "puppet apply --hiera_config={} --detailed-exitcodes --manifestdir {} {}".format(
                PurePosixPath(provisioner._guest_hiera_file),
                PurePosixPath(provisioner._guest_manifests_path),
                PurePosixPath(provisioner._guest_manifests_path) / 'site.pp')]

    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_set_module_path(self, mock_run, mock_copy_dir):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'mani.pp',
            'manifests_path': 'test_manifests',
            'module_path': 'test-puppet-modules'})
        provisioner.provision()

        assert mock_copy_dir.call_count == 2
        assert (Path('test-puppet-modules'),
                PurePosixPath(provisioner._guest_module_path)) in {
                    mock_copy_dir.call_args_list[0][0],
                    mock_copy_dir.call_args_list[1][0]}

        assert mock_run.call_count == 2
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            "puppet apply --modulepath {}:{} --detailed-exitcodes --manifestdir {} {}".format(
                PurePosixPath(provisioner._guest_module_path),
                PurePosixPath(provisioner._guest_default_module_path),
                PurePosixPath(provisioner._guest_manifests_path),
                PurePosixPath(provisioner._guest_manifests_path) / 'mani.pp')]

    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_set_environment_variables(self, mock_run, mock_copy_dir):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'site.pp',
            'manifests_path': 'test_manifests',
            'environment_variables': {'FOO': 'bah', 'BAR': 'baz baz'}})
        provisioner.provision()
        assert mock_run.call_count == 2
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            "BAR='baz baz' FOO=bah "
            "puppet apply --detailed-exitcodes --manifestdir {} {}".format(
                PurePosixPath(provisioner._guest_manifests_path),
                PurePosixPath(provisioner._guest_manifests_path) / 'site.pp')]

    @unittest.mock.patch.object(Guest, 'copy_directory')
    @unittest.mock.patch.object(Guest, 'run')
    def test_can_set_options(self, mock_run, mock_copy_dir):
        class DummyGuest(Guest):
            name = 'dummy'
        host = Host()
        guest = DummyGuest(unittest.mock.Mock())
        mock_run.return_value = 0
        provisioner = PuppetProvisioner('./', host, [guest], {
            'manifest_file': 'site.pp',
            'manifests_path': 'test_manifests',
            'options': '--a --c="test space" --b'})
        provisioner.provision()
        assert mock_run.call_count == 2
        assert mock_run.call_args_list[1][0][0] == [
            'sh', '-c',
            """puppet apply --a '--c=test space' --b """
            """--detailed-exitcodes --manifestdir {} {}""".format(
                PurePosixPath(provisioner._guest_manifests_path),
                PurePosixPath(provisioner._guest_manifests_path) / 'site.pp')]
