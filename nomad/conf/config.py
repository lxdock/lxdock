# -*- coding: utf-8 -*-

import logging
import os

import yaml

from . import constants
from .exceptions import ConfigFileNotFound

logger = logging.getLogger(__name__)


class Config(object):
    """ Holds the configuration of a LXD-Nomad project. """

    def __init__(self, base_dir, filename):
        self.base_dir = base_dir
        self.filename = filename
        self.containers = []
        self._dict = {}

    def __getitem__(self, key):
        return self._dict[key]

    @classmethod
    def from_base_dir(cls, base_dir):
        """ Returns a Config instance using a base directory. """
        existing_config_filenames = [
            filename for filename in constants.ALLOWED_FILENAMES
            if os.path.exists(os.path.join(base_dir, filename))]

        if not existing_config_filenames:
            raise ConfigFileNotFound

        config_filename = os.path.join(base_dir, existing_config_filenames[0])
        if len(existing_config_filenames) > 1:
            logger.warn('Multiple config files were found: {0}'.format(
                ', '.join(existing_config_filenames)))
            logger.warn('Using: {0}'.format(config_filename))

        # Initializes the config instance.
        config = cls(base_dir, config_filename)
        # Loads the YML.
        # Note/TODO: some validation checks should be triggered here.
        config.load()
        # Loads the containers.
        config.load_containers()

        return config

    def load(self):
        """ Loads the YML configuration file and store it inside the `_dict` dictionary. """
        self._dict = self._load_yml()

    def load_containers(self):
        """ Loads each container configuration and store it inside the `containers` attribute. """
        # TODO: support multiple containers
        # For now we consider that the configuration file holds only one container, so we just pass
        # the full dictionary to initialize the `ContainerConfig` instance.
        self.containers.append(ContainerConfig(self._dict))

    def _load_yml(self):
        """ Loads the YML configuration file. """
        with open(self.filename, 'r') as fp:
            return yaml.safe_load(fp)
        # TODO: handle potential errors here


class ContainerConfig(dict):
    """ Holds the specific configuration of a container. """
