import logging
import os
from pathlib import Path

import yaml
from voluptuous.error import Invalid

from . import constants
from .exceptions import ConfigFileNotFoundError, ConfigFileValidationError
from .schema import schema

logger = logging.getLogger(__name__)


class Config(object):
    """ Holds the configuration of a LXDock project. """

    def __init__(self, homedir, filename):
        self.homedir = homedir
        self.filename = filename
        self.containers = []
        self._dict = {}

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        return self._dict[key]

    @classmethod
    def from_base_dir(cls, base_dir='.'):
        """ Returns a Config instance using a base directory. """
        base_dir_path = Path(os.path.abspath(base_dir))
        candidate_paths = [base_dir_path, ] + list(base_dir_path.parents)
        existing_config_paths = []
        for candidate_path in candidate_paths:
            existing_config_paths = [
                os.path.join(str(candidate_path), filename)
                for filename in constants.ALLOWED_FILENAMES
                if os.path.exists(os.path.join(str(candidate_path), filename))]
            if existing_config_paths:
                break

        if not existing_config_paths:
            raise ConfigFileNotFoundError(
                'Unable to find a suitable configuration file in this directory. '
                'Are you in the right directory?\n'
                'The supported filenames are: {}'.format(', '.join(constants.ALLOWED_FILENAMES))
            )

        config_dirname, config_filename = os.path.split(existing_config_paths[0])
        if len(existing_config_paths) > 1:
            logger.warn('Multiple config files were found: {0}'.format(
                ', '.join([os.path.split(p)[1] for p in existing_config_paths])))
            logger.warn('Using: {0}'.format(config_filename))

        # Initializes the config instance.
        config = cls(config_dirname, config_filename)

        # Loads the YML.
        config.load()

        # Validates the content of the configuration. We chdir into the home directory of the
        # project in order to ensure that IsFile/IsDir validators keep working properly if the
        # config is initialized from a subfolder of the project.
        cwd = os.getcwd()
        os.chdir(config.homedir)
        try:
            schema(config._dict)
        except Invalid as e:
            # Formats the voluptuous error
            path = ' @ %s' % '.'.join(map(str, e.path)) if e.path else ''
            msg = 'The LXDock file is invalid because: {0}'.format(e.msg + path)
            raise ConfigFileValidationError(msg)
        finally:
            os.chdir(cwd)

        # Loads the containers.
        config.load_containers()

        return config

    def load(self):
        """ Loads the YML configuration file and store it inside the `_dict` dictionary. """
        self._dict = self._load_yml()

    def load_containers(self):
        """ Loads each container configuration and store it inside the `containers` attribute. """
        containers = [ContainerConfig(self._get_container_config_dict(cdict))
                      for cdict in self._dict.get('containers', [])]
        # If we cannot consider multiple containers, we just pass the full dictionary to initialize
        # the `ContainerConfig` instance.
        if not len(containers):
            unique_container_config = ContainerConfig(self._dict)
            # We associate a specific name to the unique container if it wasn't explicitly defined
            # under the 'containers' section of the LXDock file.
            unique_container_config['name'] = 'default'
            containers = [unique_container_config, ]

        self.containers.extend(containers)

    def serialize(self):
        """ Returns the configuration as a string. """
        return yaml.dump(self._dict, default_flow_style=False)

    def _get_container_config_dict(self, container_dict):
        """ Returns a dictionary containing the container's configuration.

        The dictionary that is returned contains the container's configuration and the global config
        values. These global values can be defined outside of the scope of the container's config
        and can be used by each container.
        """
        container_config = dict(self._dict)
        container_config.update(container_dict)
        del container_config['containers']
        return container_config

    def _load_yml(self):
        """ Loads the YML configuration file. """
        with open(os.path.join(self.homedir, self.filename), 'r') as fp:
            return yaml.safe_load(fp)
        # TODO: handle potential errors here


class ContainerConfig(dict):
    """ Holds the specific configuration of a container. """
