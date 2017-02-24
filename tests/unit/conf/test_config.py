import os
import pytest

from lxdock.conf.config import Config
from lxdock.conf.exceptions import ConfigFileNotFoundError, ConfigFileValidationError


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestConfig:
    def test_can_be_initialized_from_a_base_dir(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project01')
        config = Config.from_base_dir(project_dir)
        assert config['name'] == 'project01'
        assert config['image'] == 'ubuntu/xenial'
        assert config['mode'] == 'pull'

    def test_works_if_multiple_config_files_are_found(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project_with_multiple_config_files')
        config = Config.from_base_dir(project_dir)
        assert config.filename == os.path.join(project_dir, 'lxdock.yml')

    def test_raises_an_error_if_the_config_file_cannot_be_found(self):
        project_dir = os.path.dirname(__file__)
        with pytest.raises(ConfigFileNotFoundError):
            Config.from_base_dir(project_dir)

    def test_raises_an_error_if_the_config_file_is_invalid(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project_with_invalid_config')
        with pytest.raises(ConfigFileValidationError):
            Config.from_base_dir(project_dir)

    def test_allows_to_get_items_from_config_dict(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project01')
        config = Config.from_base_dir(project_dir)
        assert config['name'] == 'project01'

    def test_allows_to_check_item_presence_in_config_dict(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project01')
        config = Config.from_base_dir(project_dir)
        assert 'name' in config

    def test_can_load_container_config_from_top_level_options_if_no_containers_are_defined(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project01')
        config = Config.from_base_dir(project_dir)
        assert config.containers == [
            {'image': 'ubuntu/xenial', 'mode': 'pull', 'name': 'default'},
        ]

    def test_can_properly_handle_configurations_defining_multiple_containers(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project02')
        config = Config.from_base_dir(project_dir)
        assert config.containers == [
            {'mode': 'pull', 'image': 'ubuntu/xenial', 'name': 'web'},
            {
                'mode': 'pull', 'hostnames': ['ci.local'], 'image': 'debian/jessie', 'name': 'ci',
                'privileged': True,
            },
        ]

    def test_can_serialize_the_parsed_config(self):
        project_dir = os.path.join(FIXTURE_ROOT, 'project01')
        config = Config.from_base_dir(project_dir)
        assert config.serialize() == 'image: ubuntu/xenial\nmode: pull\nname: project01\n'
