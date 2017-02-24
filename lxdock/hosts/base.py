"""
    Base host
    =========
    This module provides the `Host` base class that is used to define the host OS or distributions
    supported by LXDock.
"""

import os
import platform
import subprocess
from pathlib import Path

from ..utils.lxd import get_lxd_dir
from ..utils.metaclass import with_metaclass

__all__ = ['Host', ]


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

    def __init__(self, lxd_container):
        self.lxd_container = lxd_container

    @classmethod
    def detect(cls):
        """ Detects if the host is an "instance" of the considered OS/distribution. """
        return cls.name.lower() in platform.platform().lower()

    def get_ssh_pubkey(self):
        """ Returns the SSH public key of the current user or None if it cannot be found. """
        pubkey_path = Path(os.path.expanduser('~/.ssh/id_rsa.pub'))
        try:
            return pubkey_path.open().read()
        except FileNotFoundError:  # pragma: no cover
            pass

    def give_current_user_access_to_share(self, source):
        """ Give read/write access to `source` for the current user. """
        subprocess.Popen('setfacl -Rdm u:{}:rwX {}'.format(os.getuid(), source), shell=True).wait()

    def give_mapped_user_access_to_share(self, source, userpath=None):
        """ Give read/write access to `source` for the mapped user owning `userpath`.

        `userpath` is a path that is relative to the LXD base directory (where LXD store contaners).
        """
        # LXD uses user namespaces when running safe containers. This means that it maps a set of
        # uids and gids on the host to a set of uids and gids in the container.
        # When considering unprivileged containers we want to ensure that the "root user" (or any
        # other user) of such containers have the proper rights to write in shared folders. To do so
        # we have to retrieve the UserID on the host-side that is mapped to the "root"'s UserID (or
        # any other user's UserID) on the guest-side. This will allow to set ACL on the host-side
        # for this UID. By doing this we will also allow "root" user on the guest-side to read/write
        # in shared folders.
        container_path_parts = [get_lxd_dir(), 'containers', self.lxd_container.name, 'rootfs']
        container_path_parts += userpath.split('/') if userpath else []
        container_path = os.path.join(*container_path_parts)
        container_path_stats = os.stat(container_path)
        host_userpath_uid = container_path_stats.st_uid
        subprocess.Popen(
            'setfacl -Rm user:lxd:rwx,default:user:lxd:rwx,'
            'user:{0}:rwx,default:user:{0}:rwx {1}'.format(host_userpath_uid, source),
            shell=True).wait()
