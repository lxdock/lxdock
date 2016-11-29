# -*- coding: utf-8 -*-

import logging

from .container import Container

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

    def destroy(self):
        """ Destroys the containers of the project. """
        for container in self.containers:
            container.destroy()

    def halt(self):
        """ Stops containers of the project. """
        for container in self.containers:
            container.halt()

    def provision(self):
        """ Provisions the containers of the project. """
        for container in self.containers:
            container.provision()

    def shell(self):
        """Opens a new shell in our first container. """
        self.containers[0].shell()

    def up(self):
        """ Creates, starts and provisions the containers of the project. """
        for container in self.containers:
            container.up()
