"""
    Base guest
    ==========
    This module provides the `Guest` base class that is used to define the guest OS or distributions
    supported by LXDock (eg. debian, ...).
"""

import logging
import re
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from pylxd.exceptions import NotFound

from ..utils.metaclass import with_metaclass


__all__ = ['Guest', ]

logger = logging.getLogger(__name__)


class InvalidGuest(Exception):
    """ The `Guest` subclass is not valid. """


class _GuestBase(type):
    """ Metaclass for all LXD guests.

    This metaclass ensures that all defined `Guest` subclasses have the required attributes and
    proceeds to some validation checks. Additionally it implements the "plugin mount" paradigm and
    stores a list of `Guest` subclasses in the namespace of the "plugin mount" class (`Guest`).
    """

    def __new__(cls, name, bases, attrs):
        super_new = super(_GuestBase, cls).__new__
        parents = [base for base in bases if isinstance(base, _GuestBase)]

        # We stop here if we are considering the top-level class to which this metaclass was applied
        # and not one of its subclasses (eg. Guest).
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Constructs the Guest class.
        new_guest = super_new(cls, name, bases, attrs)

        # Performs some validation checks.
        if not new_guest.name:
            raise InvalidGuest("The 'name' attribute of Guest subclasses cannot be None")

        return new_guest

    def __init__(cls, name, bases, attrs):
        # We implement the "mount point" paradigm here in order to make all `Guest` subclassses
        # available in a single attribute.
        if not hasattr(cls, 'guests'):
            # The class has no guests list: this means that we are considering the "plugin mount"
            # class. So we created the list that will hold all the defined `Guest` subclasses.
            cls.guests = []
        else:
            # The `guests` attribute already exists so we are considering a `Guest` subclass, which
            # needs to be registered.
            cls.guests.append(cls)


class Guest(with_metaclass(_GuestBase)):
    """ Represents a single guest.

    `Guest` subclasses will be used by `Container` instances to perform common operations on the
    guest side. For example they can be used to ensure that some packages are installed when doing
    barebone setups, to create some users, ... `Guest` subclasses should correspond to specific OSes
    or distributions that can be runned as LXD containers.
    """

    # The `name` of a guest is a required attribute and should always be set on `Guest` subclasses.
    name = None

    def __init__(self, container):
        self.container = container
        self.lxd_container = container._container

    @classmethod
    def detect(cls, lxd_container):
        """ Detects if the container is an "instance" of the considered OS.

        The operations defined in this method assume that OS/distribution information will be
        available through the analysis of files such as ""/etc/os-release", ""/etc/lsb_release" or
        ""/etc/issue". This classmethod should be overriden if these methods cannot be applied to
        the considered OS/distribution.
        """
        candidates = [
            ('/etc/os-release', '(id|ID)="?{}"?'.format(cls.name.lower())),
            ('/etc/lsb_release', '(id|ID)="?{}"?'.format(cls.name.lower())),
            ('/etc/issue', cls.name.lower()),
        ]
        found = False
        for candidate, pattern in candidates:
            try:
                candidate_filecontent = lxd_container.files.get(candidate)
            except NotFound:
                continue
            found = len(re.findall(pattern, str(candidate_filecontent.lower()))) > 0
            if found:
                break
        return found

    @classmethod
    def get(cls, container):
        """ Returns the `Guest` instance associated with the considered container. """
        class_ = next((k for k in cls.guests if k.detect(container._container)), Guest)
        return class_(container)

    def add_ssh_pubkey_to_root_authorized_keys(self, pubkey):
        """ Add a given SSH public key to the root user's authorized keys. """
        logger.info("Adding {} to machine's authorized keys".format(pubkey))
        self.run(['mkdir', '-p', '/root/.ssh'])
        self.lxd_container.files.put('/root/.ssh/authorized_keys', pubkey)

    def create_user(self, username, home=None, password=None):
        """ Adds the passed user to the container system. """
        options = ['--create-home', ]
        if home is not None:
            options += ['--home-dir', home, ]
        if password is not None:
            options += ['-p', password, ]
        self.run(['useradd', ] + options + [username, ])

    ########################################################
    # METHODS THAT SHOULD BE OVERRIDEN IN GUEST SUBCLASSES #
    ########################################################

    def install_packages(self, packages):  # pragma: no cover
        """ Installs the considered packages on the guest.

        :param packages: The list of packages to install on the guest
        :type packages: list
        """
        # This method should be overriden in `Guest` subclasses.
        self._warn_guest_not_supported('for installing packages')

    ##################
    # HELPER METHODS #
    ##################

    def run(self, cmd_args):
        """ Runs the specified command inside the current container. """
        logger.debug('Running {0}'.format(' '.join(cmd_args)))
        exit_code, stdout, stderr = self.lxd_container.execute(cmd_args)
        logger.debug(stdout)
        logger.debug(stderr)
        return exit_code

    def copy_file(self, host_path, guest_path):
        """
        Copies a file from host_path (pathlib.Path) to guest_path (pathlib.PurePath).
        Ensures `mkdir -p` before calling LXD file put.
        """
        self.run(['mkdir', '-p', str(guest_path.parent)])
        with host_path.open('rb') as f:
            logger.debug('Copying host:{} to guest:{}'.format(host_path, guest_path))
            self.lxd_container.files.put(str(guest_path), f.read())

    _guest_temporary_tar_path = '/.lxdock.d/copied_directory.tar'

    def copy_directory(self, host_path, guest_path):
        """
        Copies a directory from host_path (pathlib.Path) to guest_path (pathlib.PurePath).
        This is natively supported since LXD 2.2 but we have to support 2.0+
        Refs: https://github.com/lxc/lxd/issues/2401

        Uses tar to pack/unpack the directory.
        """
        guest_tar_path = self._guest_temporary_tar_path
        self.run(['mkdir', '-p', str(guest_path)])
        with tempfile.NamedTemporaryFile() as f:
            logger.debug("Creating tar file from {}".format(host_path))
            tar = tarfile.open(f.name, 'w')
            tar.add(str(host_path), arcname='.')
            tar.close()
            self.copy_file(Path(f.name), PurePosixPath(guest_tar_path))
        self.run(['tar', '-xf', guest_tar_path, '-C', str(guest_path)])
        self.run(['rm', '-f', str(guest_tar_path)])

    ##################################
    # PRIVATE METHODS AND PROPERTIES #
    ##################################

    def _warn_guest_not_supported(self, for_msg):  # pragma: no cover
        """ Warns the user that a specific operation cannot be performed. """
        logger.warn('Guest not supported {}, doing nothing...'.format(for_msg))
