import os
import pytest

from nomad.conf.config import Config
from nomad.conf.exceptions import ConfigFileNotFoundError, ConfigFileValidationError


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
        assert config.filename == os.path.join(project_dir, 'nomad.yml')

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
