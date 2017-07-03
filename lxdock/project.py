import logging

from . import constants
from .container import Container
from .exceptions import ProjectError
from .guests import Guest
from .hosts import Host
from .logging import (console_stderr_handler, console_stdout_handler, get_default_formatter,
                      get_per_container_formatter)
from .network import ContainerEtcHosts, EtcHosts
from .provisioners import Provisioner


logger = logging.getLogger(__name__)


class Project:
    """ A project is used to orchestrate a collection of containers. """

    def __init__(self, name, homedir, client, containers, provisioning_steps):
        self.name = name
        self.homedir = homedir
        self.client = client
        self.containers = containers
        self.provisioning_steps = provisioning_steps

    @classmethod
    def from_config(cls, project_name, client, config):
        """ Creates a `Project` instance from a config object. """
        containers = []
        for container_config in config.containers:
            containers.append(Container(project_name, config.homedir, client, **container_config))
        return cls(project_name, config.homedir, client, containers, config.provisioning_steps)

    #####################
    # CONTAINER ACTIONS #
    #####################

    def destroy(self, container_names=None):
        """ Destroys the containers of the project. """
        containers = [self.get_container_by_name(name) for name in container_names] \
            if container_names else self.containers
        for container in self._containers_generator(containers=containers):
            container.destroy()
        self._update_guest_etchosts()

    def halt(self, container_names=None):
        """ Stops containers of the project. """
        containers = [self.get_container_by_name(name) for name in container_names] \
            if container_names else self.containers
        for container in self._containers_generator(containers=containers):
            container.halt()
        self._update_guest_etchosts()

    def provision(self, container_names=None, force=True):
        """ Provisions the containers of the project. """
        # This happens in two phases: local provisioning, then global provisioning.
        # Local provisioning is the provisioning that is declared directly in the
        # `containers` config section. Global provisioning is declared at the root
        # of the config.
        containers = [self.get_container_by_name(name) for name in container_names] \
            if container_names else self.containers
        for container in self._containers_generator(containers=containers):
            container.provision(force=force)

        host = Host.get()
        if not force:
            containers = [c for c in containers if not c.is_provisioned]
        if not containers:
            return

        guests = [Guest.get(c) for c in containers]
        for provisioning_item in self.provisioning_steps:
            provisioning_type = provisioning_item['type'].lower()
            provisioner_class = Provisioner.provisioners.get(provisioning_type)
            if provisioner_class is not None:
                provisioner = provisioner_class(
                    self.homedir, host, guests, provisioning_item)
                logger.info('Global provisioning with {0}'.format(provisioner.name))
                provisioner.provision()

        for guest in guests:
            guest.lxd_container.config['user.lxdock.provisioned'] = 'true'
            guest.lxd_container.save(wait=True)

    def shell(self, container_name=None, **kwargs):
        """ Opens a new shell in our first container. """
        containers = [self.get_container_by_name(container_name)] if container_name \
            else self.containers
        if len(containers) > 1:
            raise ProjectError(
                'This action requires a container name to be specified because {count} '
                'containers are defined in this project.'.format(count=len(self.containers)))
        for container in self._containers_generator(containers=containers):
            container.shell(**kwargs)

    def status(self, container_names=None):
        """ Shows the statuses of the containers of the project. """
        containers = [self.get_container_by_name(name) for name in container_names] \
            if container_names else self.containers
        max_name_length = max(len(c.name) for c in containers)
        logger.info('Current container states:')
        for container in containers:
            logger.info('{container_name} ({status})'.format(
                container_name=container.name.ljust(max_name_length + 10), status=container.status))

    def up(self, container_names=None, provisioning_mode=None):
        """ Creates, starts and provisions the containers of the project. """
        containers = [self.get_container_by_name(name) for name in container_names] \
            if container_names else self.containers
        not_running = [c for c in containers if not c.is_running]
        if not not_running:
            logger.warning("Everything is already up and running! Nothing to do.")
            return
        [logger.info('Bringing container "{}" up'.format(c.name)) for c in not_running]
        for container in self._containers_generator(containers=not_running):
            container.up()
        self._update_guest_etchosts()

        # Provisions the container if applicable; that is only if it hasn't been provisioned before
        # or if the provisioning is manually enabled.
        provisioning_mode = provisioning_mode or constants.ProvisioningMode.AUTO
        if not provisioning_mode == constants.ProvisioningMode.DISABLED:
            force = provisioning_mode == constants.ProvisioningMode.ENABLED
            self.provision(container_names=[c.name for c in not_running], force=force)

    ##################################
    # UTILITY METHODS AND PROPERTIES #
    ##################################

    def get_container_by_name(self, name):
        """ Returns the `Container` instance associated with the given name. """
        containers_dict = {c.name: c for c in self.containers}
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
            console_stdout_handler.setFormatter(get_per_container_formatter(container.name))
            console_stderr_handler.setFormatter(get_per_container_formatter(container.name))
            yield container
        console_stdout_handler.setFormatter(get_default_formatter())
        console_stderr_handler.setFormatter(get_default_formatter())

    def _update_guest_etchosts(self):
        """ Updates /etc/hosts on **all** running lxdock-managed containers.

        ... even those outside the current project. This way, containers can contact themselves
        using the same domain names the host uses.
        """
        def should_update(c):
            return c.config.get('user.lxdock.made') and c.status_code == constants.CONTAINER_RUNNING
        # At this point, our host's /etc/hosts is fully updated. No need to go fetch IP's and stuff
        # we can just re-use what we've already computed in every container up/halt ops before.
        etchosts = EtcHosts()
        containers = (c for c in self.client.containers.all() if should_update(c))
        for container in containers:
            container_etchosts = ContainerEtcHosts(container)
            container_etchosts.lxdock_bindings = etchosts.lxdock_bindings
            container_etchosts.save()
