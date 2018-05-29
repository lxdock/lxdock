import logging
import os
from pathlib import Path

import yaml
from dotenv.main import dotenv_values
from voluptuous.error import Invalid

from . import constants
from .exceptions import (ConfigFileInterpolationError, ConfigFileNotFoundError,
                         ConfigFileValidationError)
from .interpolation import interpolate_variables
from .schema import schema


logger = logging.getLogger(__name__)


class Config:
    """ Holds the configuration of a LXDock project. """

    def __init__(self, homedir, filename):
        self.homedir = homedir
        self.filename = filename
        self.containers = []
        self.provisioning_steps = []
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
            logger.warning('Multiple config files were found: {0}'.format(
                ', '.join([os.path.split(p)[1] for p in existing_config_paths])))
            logger.warning('Using: {0}'.format(config_filename))

        # Initializes the config instance.
        config = cls(config_dirname, config_filename)

        # Loads the YML.
        config.load()

        # Validates the content of the configuration. We chdir into the home directory of the
        # project in order to ensure that IsFile/IsDir validators keep working properly if the
        # config is initialized from a subfolder of the project.
        cwd = os.getcwd()
        os.chdir(config.homedir)

        # Performs variable substitution / interpolation in the configuration values.
        config.interpolate()

        try:
            config._dict = schema(config._dict)
        except Invalid as e:
            # Formats the voluptuous error
            path = ' @ %s' % '.'.join(map(str, e.path)) if e.path else ''
            msg = 'The LXDock file is invalid because: {0}'.format(e.msg + path)
            raise ConfigFileValidationError(msg)
        finally:
            os.chdir(cwd)

        config.extract_config_from_dict()

        return config

    def interpolate(self):
        """ Interpolates the considered config.

        In order to perform this variable substitution LXDock will use environment variables plus
        some other pre-defined variables. The later will be injected in the context used to perform
        this interpolation.
        """
        # Builds a dictionary of variables that will be used to perform variable substitution in the
        # config values.
        mapping = {}
        mapping.update(os.environ)

        # Fetches variables that could be defined in a .env file and inserts them in the mapping.
        env_filepath = os.path.join(self.homedir, '.env')
        if os.path.exists(env_filepath):
            mapping.update(dotenv_values(env_filepath))

        # Inserts LXDock special variables into the final mapping.
        mapping.update({
            # The absolute path toward the home directory of the LXDock project is injected into
            # the mapping used to perform variable substitution in the initial config.
            # This can be useful to reference paths that are relative to the project's root
            # directory in LXDock file options such as inline commands.
            'LXDOCK_YML_DIR': self.homedir,
        })

        try:
            self._dict = interpolate_variables(self._dict, mapping)
        except KeyError as e:
            raise ConfigFileInterpolationError(
                'Variable substitution failed when parsing the LXDock file. The failing variable '
                'name is: ${}'.format(e.args[0]))

    def load(self):
        """ Loads the YML configuration file and store it inside the `_dict` dictionary. """
        self._dict = self._load_yml()

    def extract_config_from_dict(self):
        """ Take config from the _dict and place them into ready-to-use config in `self`. """
        containers = [ContainerConfig(self._get_container_config_dict(cdict))
                      for cdict in self._dict.get('containers', [])]
        # If we cannot consider multiple containers, we just pass the full dictionary to initialize
        # the `ContainerConfig` instance.
        if not len(containers):
            unique_container_config = ContainerConfig(self._dict)
            # We don't inherit global provisioning in specific container config.
            if 'provisioning' in unique_container_config:
                del unique_container_config['provisioning']

            # We associate a specific name to the unique container if it wasn't explicitly defined
            # under the 'containers' section of the LXDock file.
            unique_container_config['name'] = 'default'
            containers = [unique_container_config, ]

        self.containers.extend(containers)

        self.provisioning_steps = self._dict.get('provisioning', [])

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

        # We don't inherit global provisioning in specific container config.
        if 'provisioning' in container_config:
            del container_config['provisioning']

        # If both global and container scope contains lxc_config, merge them
        lxck = 'lxc_config'
        if lxck in container_config and lxck in container_dict:
            container_dict = dict(container_dict)
            container_config[lxck].update(container_dict[lxck])
            del container_dict[lxck]

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
