import copy
import logging
import os
import subprocess
import textwrap
import time
from functools import wraps
from pathlib import PurePosixPath

from pylxd.exceptions import LXDAPIException, NotFound

from . import constants
from .exceptions import ContainerOperationFailed
from .guests import Guest
from .hosts import Host
from .network import EtcHosts, get_ip
from .provisioners import Provisioner
from .utils.identifier import folderid


logger = logging.getLogger(__name__)


def must_be_created_and_running(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.exists:
            logger.error('The container is not created.')
            return
        elif not self.is_running:
            logger.error('The container is not running.')
            return
        return method(self, *args, **kwargs)

    return wrapper


class Container:
    """ Represents a specific container that is managed by LXDock. """

    # The default image server that will be used to pull images in "pull" mode.
    _default_image_server = 'https://images.linuxcontainers.org'

    # The default path for storing the command to execute during `lxdock shell`.
    _guest_shell_script_file = '/.lxdock.d/shell_cmd.sh'

    def __init__(self, project_name, homedir, client, **options):
        self.project_name = project_name
        self.homedir = homedir
        self.client = client
        self.options = options

    #####################
    # CONTAINER ACTIONS #
    #####################

    def destroy(self):
        """ Destroys the container. """
        container = self._get_container(create=False)
        if container is None:
            logger.info("Container doesn't exist, nothing to destroy.")
            return

        # Halts the container...
        self.halt()
        # ... and destroy it!
        logger.info('Destroying container "{name}"...'.format(name=self.name))
        container.delete(wait=True)
        logger.info('Container "{name}" destroyed!'.format(name=self.name))

    def halt(self):
        """ Stops the container. """
        if not self.exists:
            logger.info("The container doesn't exist.")
            return

        if self.is_stopped:
            logger.info('The container is already stopped.')
            return

        # Removes configurations related to container's hostnames if applicable.
        self._unsetup_hostnames()

        logger.info('Stopping...')
        try:
            self._container.stop(timeout=30, force=False, wait=True)
        except LXDAPIException:
            logger.warning("Can't stop the container. Forcing...")
            self._container.stop(force=True, wait=True)

    @must_be_created_and_running
    def provision(self, force=True):
        """ Provisions the container. """
        # We run this in case our lxdock.yml config was modified since our last `lxdock up`.
        self._setup_env()

        try:
            provisioning_steps = self.options['provisioning']
        except KeyError:
            return

        if not force and self.is_provisioned:
            return

        for provisioning_item in provisioning_steps:
            provisioning_type = provisioning_item['type'].lower()
            provisioner_class = Provisioner.provisioners.get(provisioning_type)
            if provisioner_class is not None:
                provisioner = provisioner_class(
                    self.homedir, self._host, [self._guest], provisioning_item)
                logger.info('Provisioning with {0}'.format(provisioner.name))
                provisioner.provision()

    @must_be_created_and_running
    def shell(self, username=None, command=None):
        """ Opens a new interactive shell in the container. """
        # We run this in case our lxdock.yml config was modified since our last `lxdock up`.
        self._setup_env()

        # For now, it's much easier to call `lxc`, but eventually, we might want to contribute
        # to pylxd so it supports `interactive = True` in `exec()`.
        shellcfg = self.options.get('shell', {})
        shelluser = username or shellcfg.get('user')
        if shelluser:
            cmd = 'lxc exec {} -- su -l {}'.format(self.lxd_name, shelluser)
        else:
            cmd = 'lxc exec {} -- su -l root'.format(self.lxd_name)

        # Optionally run a command and exit.
        # For multiple commands use: lxdock shell -c "command1; command2"
        if command:
            # Again, a bit of trial-and-error.
            # 1. Using `su -s SCRIPT_FILE` instead of `su -c COMMAND` because `su -c` cannot
            #    receive SIGINT (Ctrl-C).
            #    Ref: //sethmiller.org/it/su-forking-and-the-incorrect-trapping-of-sigint-ctrl-c/
            #    See also: //github.com/lxdock/lxdock/pull/67#issuecomment-299755944

            self._guest.run(['mkdir', '-p',
                             str(PurePosixPath(self._guest_shell_script_file).parent)])
            self._container.files.put(self._guest_shell_script_file, textwrap.dedent(
                """\
                #!/bin/sh
                export SHELL=/bin/sh
                {}
                """.format(command)))
            self._guest.run(['chmod', 'a+rx', self._guest_shell_script_file])
            cmd += ' -s {}'.format(self._guest_shell_script_file)

        subprocess.call(cmd, shell=True)

    def up(self):
        """ Creates, starts and provisions the container. """
        if self.is_running:
            logger.info('Container "{name}" is already running'.format(name=self.name))
            return

        logger.info('Starting container "{name}"...'.format(name=self.name))
        self._container.start(wait=True)
        if not self.is_running:
            logger.error('Something went wrong trying to start the container.')
            raise ContainerOperationFailed()

        ip = self._setup_ip()
        if not ip:
            return

        logger.info('Container "{name}" is up! IP: {ip}'.format(name=self.name, ip=ip))

        # Setup hostnames if applicable.
        self._setup_hostnames(ip)

        # Setup users if applicable.
        self._setup_users()

        # Setup shares if applicable.
        self._setup_shares()

        # Override environment variables
        self._setup_env()

    ##################################
    # UTILITY METHODS AND PROPERTIES #
    ##################################

    @property
    def exists(self):
        """ Returns True if the considered container has already been created. """
        try:
            self.client.containers.get(self.lxd_name)
        except NotFound:
            return False
        else:
            return True

    @property
    def is_privileged(self):
        """ Returns a boolean indicating if the container is privileged. """
        return self._container.config.get('security.privileged') == 'true'

    @property
    def is_provisioned(self):
        """ Returns a boolean indicating if the container is provisioned. """
        return self._container.config.get('user.lxdock.provisioned') == 'true'

    @property
    def is_running(self):
        """ Returns a boolean indicating if the container is running. """
        return self._container.status_code == constants.CONTAINER_RUNNING

    @property
    def is_stopped(self):
        """ Returns a boolean indicating if the container is stopped. """
        return self._container.status_code == constants.CONTAINER_STOPPED

    @property
    def lxd_name(self):
        """ Returns the name of the container that is used in the scope of LXD.

        This name id supposed to be unique among all the containers managed by LXD.
        """
        # Note: all container names must be a valid hostname! That is: maximum 63 characters, no
        # dots, no digit at first position, made entirely of letters/digits/hyphens, ...
        if not hasattr(self, '_lxd_name'):
            lxd_name_prefix = '{project_name}-{name}'.format(
                project_name=self.project_name, name=self.name)
            # We compute a project ID based on inode numbers in order to ensure that our LXD names
            # are unique.
            project_id = folderid(self.homedir)
            self._lxd_name = '{prefix}-{id}'.format(
                prefix=lxd_name_prefix[:63 - len(project_id)], id=project_id)
        return self._lxd_name

    @property
    def name(self):
        """ Returns the "local" name of the container. """
        return self.options['name']

    @property
    def status(self):
        """ Returns a string identifier representing the current status of the container. """
        default_status = 'undefined'  # Note: this status should not be displayed at all...
        container = self._get_container(create=False)
        if container is None:
            status = 'not-created'
        else:
            status = {
                constants.CONTAINER_RUNNING: 'running',
                constants.CONTAINER_STOPPED: 'stopped',
            }.get(container.status_code, default_status)
        return status

    ##################################
    # PRIVATE METHODS AND PROPERTIES #
    ##################################

    def _get_container(self, create=True):
        """ Gets or creates the PyLXD container. """
        try:
            container = self.client.containers.get(self.lxd_name)
        except NotFound:
            container = None
        else:
            return container

        if not create:
            return

        logger.warning('Unable to find container "{name}" for directory "{homedir}"'.format(
            name=self.name, homedir=self.homedir))

        logger.info(
            'Creating new container "{name}" '
            'from image {image}'.format(name=self.lxd_name, image=self.options['image']))
        privileged = self.options.get('privileged', False)
        mode = self.options.get('mode', 'pull')

        # Get user defined lxc configs
        lxc_config = self.options.get('lxc_config', {}).copy()

        # Overwrite any configuration settings with lxdock defaults
        lxc_config.update({
            'security.privileged': 'true' if privileged else 'false',
            'user.lxdock.made': '1',
            'user.lxdock.homedir': self.homedir,
        })

        container_config = {
            'name': self.lxd_name,
            'source': {
                'alias': self.options['image'],
                # The 'mode' defines how the container will be retrieved. In "local" mode the image
                # will be determined using a local alias. In "pull" mode the image will be fetched
                # from a remote server using a remote alias.
                'mode': mode,
                # The 'protocol' to use. LXD supports two protocol: 'lxd' (RESTful API that is used
                # between the clients and a LXD daemon) and 'simplestreams' (an image server
                # description format, using JSON to describe a list of images and allowing to get
                # image information and import images). We use "simplestreams" by default (as the
                # lxc command do).
                'protocol': self.options.get('protocol', 'simplestreams'),
                # The 'server' that should be used to fetch the images. We use the default
                # linuxcontainers server for LXC and LXD when no value is provided (and if we are
                # not in "local" mode).
                'server': (self.options.get('server', self._default_image_server) if mode == 'pull'
                           else ''),
                'type': 'image',
            },
            'config': lxc_config,
        }

        profiles = self.options.get('profiles')
        if profiles:
            container_config['profiles'] = profiles.copy()

        try:
            return self.client.containers.create(container_config, wait=True)
        except LXDAPIException as e:
            logger.error("Can't create container: {error}".format(error=e))
            raise ContainerOperationFailed()

    def _setup_env(self):
        """ Add environment overrides from the conf to our container config. """
        env_override = self.options.get('environment')
        if env_override:
            for key, value in env_override.items():
                self._container.config['environment.{}'.format(key)] = str(value)
            self._container.save(wait=True)

    def _setup_hostnames(self, ip):
        """ Configure the potential hostnames associated with the container. """
        hostnames = self.options.get('hostnames', [])
        if not hostnames:
            return

        etchosts = EtcHosts()
        for hostname in hostnames:
            logger.info('Setting {hostname} to point to {ip}.'.format(
                hostname=hostname, ip=ip))
            etchosts.ensure_binding_present(hostname, ip)
        if etchosts.changed:
            logger.info("Saving host bindings to /etc/hosts. sudo may be needed")
            etchosts.save()

    def _setup_ip(self):
        """ Setup the IP address of the considered container. """
        ip = get_ip(self._container)
        if not ip:
            network_wait_timeout = self.options.get("extras", {}).get("network_wait_timeout", 10)
            logger.info('No IP yet, waiting for at most {} seconds...'.format(network_wait_timeout))
            ip = self._wait_for_ip(network_wait_timeout)
        if not ip:
            logger.warning('STILL no IP! Container is up, but probably broken.')
            logger.info('Maybe that restarting it will help? Not trying to provision.')
        return ip

    def _setup_shares(self):
        """ Setup the shared folders associated with the container. """
        if 'shares' not in self.options:
            return

        logger.info('Setting up shares...')

        if not self._host.has_subuidgid_been_set():
            raise ContainerOperationFailed()

        container = self._container

        # First, let's make an inventory of shared sources that were already there.
        existing_shares = {
            k: d for k, d in container.devices.items() if k.startswith('lxdockshare')
        }

        # Let's get rid of previously set up lxdock shares.
        for k in existing_shares:
            del container.devices[k]

        for i, share in enumerate(self.options.get('shares', []), start=1):
            source = os.path.join(self.homedir, share['source'])
            shareconf = {'type': 'disk', 'source': source, 'path': share['dest'], }

            extra_properties = share.pop('share_properties', {})
            extra_properties.pop("type", None)
            extra_properties.pop("source", None)
            extra_properties.pop("path", None)
            shareconf.update(extra_properties)

            # Upstream issue: https://github.com/lxc/lxd/issues/4538
            if shareconf.get("optional", "false").lower() in {"true", "1", "on", "yes"}:
                if not os.path.exists(source):
                    continue

            container.devices['lxdockshare%s' % i] = shareconf

        guest_username = self.options.get("users", [{"name": "root"}])[0]["name"]
        host_uid, host_gid = self._host.uidgid()
        guest_uid, guest_gid = self._guest.uidgid(guest_username)
        raw_idmap = "uid {} {}\ngid {} {}".format(host_uid, guest_uid, host_gid, guest_gid)
        raw_idmap_updated = container.config.get("raw.idmap") != raw_idmap
        if raw_idmap_updated:
            container.config["raw.idmap"] = raw_idmap

        container.save(wait=True)

        if raw_idmap_updated:
            # the container must be restarted for this to take effect
            logger.info(
              "share uid map (raw.idmap) updated, container must be restarted to take effect"
            )
            container.restart(wait=True)
            self._setup_ip()

    def _setup_users(self):
        """ Creates users defined in the container's options if applicable. """
        users = self.options.get('users', [])
        if not users:
            return

        logger.info('Ensuring users are created...')
        for user_config in users:
            config = copy.copy(user_config)
            name = config.pop('name')
            self._guest.create_user(name, **config)

    def _unsetup_hostnames(self):
        """ Removes the configuration associated with the hostnames of the container. """
        hostnames = self.options.get('hostnames', [])
        if not hostnames:
            return

        etchosts = EtcHosts()
        for hostname in hostnames:
            logger.info('Unsetting {hostname}. sudo needed.'.format(hostname=hostname))
            etchosts.ensure_binding_absent(hostname)
        if etchosts.changed:
            etchosts.save()

    def _wait_for_ip(self, seconds=10):
        """ Waits some time before trying to get the IP of the container and returning it. """
        for i in range(seconds):
            time.sleep(1)
            ip = get_ip(self._container)
            if ip:
                return ip
        return ''

    @property
    def _container(self):
        """ Returns the PyLXD Container instance associated with the considered container. """
        if not hasattr(self, '_pylxd_container'):
            self._pylxd_container = self._get_container()
        return self._pylxd_container

    @property
    def _guest(self):
        """ Returns the `Guest` instance associated with the considered container. """
        if not hasattr(self, '_container_guest'):
            self._container_guest = Guest.get(self)
        return self._container_guest

    @property
    def _host(self):
        """ Returns the `Host` instance associated with the considered host. """
        if not hasattr(self, '_container_host'):
            self._container_host = Host.get()
        return self._container_host
