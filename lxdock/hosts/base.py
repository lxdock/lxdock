"""
    Base host
    =========
    This module provides the `Host` base class that is used to define the host OS or distributions
    supported by LXDock.
"""

import logging
import os
import platform
import shlex
import subprocess
from pathlib import Path

from ..utils.metaclass import with_metaclass


__all__ = ['Host', ]

logger = logging.getLogger(__name__)


class InvalidHost(Exception):
    """ The `Host` subclass is not valid. """


class _HostBase(type):
    """ Metaclass for all LXD hosts.

    This metaclass ensures that all defined `Host` subclasses have the required attributes and
    proceeds to some validation checks. Additionally it implements the "plugin mount" paradigm and
    stores a list of `Host` subclasses in the namespace of the "plugin mount" class (`host`).
    """

    def __new__(cls, name, bases, attrs):
        super_new = super(_HostBase, cls).__new__
        parents = [base for base in bases if isinstance(base, _HostBase)]

        # We stop here if we are considering the top-level class to which this metaclass was applied
        # and not one of its subclasses (eg. Host).
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Constructs the Host class.
        new_host = super_new(cls, name, bases, attrs)

        # Performs some validation checks.
        if not new_host.name:
            raise InvalidHost("The 'name' attribute of Host subclasses cannot be None")

        return new_host

    def __init__(cls, name, bases, attrs):
        # We implement the "mount point" paradigm here in order to make all `Host` subclassses
        # available in a single attribute.
        if not hasattr(cls, 'hosts'):
            # The class has no hosts list: this means that we are considering the "plugin mount"
            # class. So we created the list that will hold all the defined `Host` subclasses.
            cls.hosts = []
        else:
            # The `hosts` attribute already exists so we are considering a `Host` subclass, which
            # needs to be registered.
            cls.hosts.append(cls)


class Host(with_metaclass(_HostBase)):
    """ Represents a single host.

    `Host` subclasses will be used by `Container` instances to perform common operations on the
    host side. For example they can be used to retrieve some date (SSH pukeys, ...) or to set up
    contaianers' hosts in the /etc/hosts file. `Host` subclasses should correspond to specific OSes
    or distributions that can be used to run LXD and LXDock.
    """

    # The `name` of a host is a required attribute and should always be set on `Host` subclasses.
    name = None

    @classmethod
    def detect(cls):
        """ Detects if the host is an "instance" of the considered OS/distribution. """
        return cls.name.lower() in platform.platform().lower()

    @classmethod
    def get(cls):
        """ Returns the `Host` instance associated with the considered host. """
        class_ = next((k for k in Host.hosts if k.detect()), Host)
        return class_()

    def get_ssh_pubkey(self):
        """ Returns the SSH public key of the current user or None if it cannot be found. """
        ssh_key_types = ['ed25519', 'rsa', 'ecdsa']
        for ssh_key_type in ssh_key_types:
            pubkey_path = Path(os.path.expanduser('~/.ssh/id_{}.pub'.format(ssh_key_type)))
            try:
                return pubkey_path.open().read()
            except FileNotFoundError:  # pragma: no cover
                pass

    def uidgid(self):
        return os.getuid(), os.getgid()

    def has_subuidgid_been_set(self):
        # Setup host subuid and subgid mapping
        # For more information, see
        # https://stgraber.org/2017/06/15/custom-user-mappings-in-lxd-containers/

        host_uid, host_gid = self.uidgid()
        subuid_lines = ["lxd:{}:1".format(host_uid), "root:{}:1".format(host_uid)]
        subgid_lines = ["lxd:{}:1".format(host_gid), "root:{}:1".format(host_gid)]

        configured_correctly = True

        with open("/etc/subuid") as f:
            subuid_content = f.read()

        for line in subuid_lines:
            if line not in subuid_content:
                logger.error("/etc/subuid missing the line: {}".format(line))
                configured_correctly = False

        with open("/etc/subgid") as f:
            subgid_content = f.read()

        for line in subgid_lines:
            if line not in subgid_content:
                logger.error("/etc/subgid missing the line: {}".format(line))
                configured_correctly = False

        if not configured_correctly:
            logger.error(
              "you must set these lines and then restart the lxd daemon before continuing"
            )

        return configured_correctly

    ##################
    # HELPER METHODS #
    ##################

    def run(self, cmd_args):
        """ Runs the specified command on the host. """
        cmd = ' '.join(map(shlex.quote, cmd_args))
        logger.debug('Running {0} on the host'.format(cmd))
        subprocess.Popen(cmd, shell=True).wait()
