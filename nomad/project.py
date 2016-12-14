# -*- coding: utf-8 -*-

import logging

from .container import Container
from .exceptions import ProjectError
from .logging import console_handler

logger = logging.getLogger(__name__)


class Project(object):
    """ A project is used to orchestrate a collection of containers. """

    def __init__(self, name, homedir, client, containers):
        self.name = name
        self.homedir = homedir
        self.client = client
        self.containers = containers

    @classmethod
    def from_config(cls, project_name, homedir, client, config):
        """ Creates a `Project` instance from a config object. """
        containers = []
        for container_config in config.containers:
            containers.append(Container(project_name, homedir, client, **container_config))
        return cls(project_name, homedir, client, containers)

    #####################
    # CONTAINER ACTIONS #
    #####################

    def destroy(self, container_name=None):
        """ Destroys the containers of the project. """
        containers = [self.get_container_by_name(container_name)] if container_name \
            else self.containers
        for container in self._containers_generator(containers=containers):
            container.destroy()

    def halt(self, container_name=None):
        """ Stops containers of the project. """
        containers = [self.get_container_by_name(container_name)] if container_name \
            else self.containers
        for container in self._containers_generator(containers=containers):
            container.halt()

    def provision(self, container_name=None):
        """ Provisions the containers of the project. """
        containers = [self.get_container_by_name(container_name)] if container_name \
            else self.containers
        for container in self._containers_generator(containers=containers):
            container.provision()

    def shell(self, container_name=None):
        """ Opens a new shell in our first container. """
        containers = [self.get_container_by_name(container_name)] if container_name \
            else self.containers
        if len(containers) > 1:
            raise ProjectError(
                'This action requires a container name to be specified because {count} '
                'containers are defined in this project.'.format(count=len(self.containers)))
        containers[0].shell()

    def up(self, container_name=None):
        """ Creates, starts and provisions the containers of the project. """
        containers = [self.get_container_by_name(container_name)] if container_name \
            else self.containers
        [logger.info('Bringing container "{}" up'.format(c.name)) for c in containers]
        for container in self._containers_generator(containers=containers):
            container.up()

    ##################################
    # UTILITY METHODS AND PROPERTIES #
    ##################################

    def get_container_by_name(self, name):
        """ Returns the `Container` instance associated with the given name. """
        containers_dict = {
            c.container_name: c for c in self.containers if c.container_name is not None}
        if name in containers_dict:
            return containers_dict[name]

        # No containers exist for the considered name.
        raise ProjectError(
            'The container with the name "{name}" was not '
            'found for this project.'.format(name=name))

    ##################################
    # PRIVATE METHODS AND PROPERTIES #
    ##################################

    def _containers_generator(self, containers=None):
        containers = containers or self.containers
        for container in containers:
            console_handler.setFormatter(logging.Formatter(
                '==> {name}: %(message)s'.format(name=container.name)))
            yield container
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(console_handler)
