import os
import shlex

from voluptuous import Any, Exclusive, IsFile

from .base import Provisioner


class ShellProvisioner(Provisioner):
    """ Allows to perform provisioning shell operations on the host/guest sides. """

    name = 'shell'
    schema = {
        Exclusive('inline', 'shelltype'): str,
        Exclusive('script', 'shelltype'): IsFile(),
        'side': Any('guest', 'host'),
    }

    def provision(self):
        """ Executes the shell commands in the guest container or in the host. """
        if 'script' in self.options and self._is_for_guest:
            # First case: we have to run the script inside the container. So the first step is
            # to copy the content of the script to a temporary file in the container, ensure
            # that the script is executable and then run the script.
            guest_scriptpath = os.path.join('/tmp/', os.path.basename(self.options['script']))
            with open(self.homedir_expanded_path(self.options['script'])) as fd:
                self.guest.lxd_container.files.put(guest_scriptpath, fd.read())
            self.guest.run(['chmod', '+x', guest_scriptpath])
            self.guest.run([guest_scriptpath, ])
        elif 'script' in self.options and self._is_for_host:
            # Second case: the script is executed on the host side.
            self.host.run([self.homedir_expanded_path(self.options['script']), ])
        elif 'inline' in self.options:
            # Final case: we run a command directly inside the container or outside.
            host_or_guest = getattr(self, self._side)
            host_or_guest.run(shlex.split(self.options['inline']))

    ##################################
    # PRIVATE METHODS AND PROPERTIES #
    ##################################

    @property
    def _is_for_guest(self):
        """ Returns True if this provisioner should run on the guest side. """
        return self._side == 'guest'

    @property
    def _is_for_host(self):
        """ Returns True if this provisioner should run on the host side. """
        return self._side == 'host'

    @property
    def _side(self):
        return self.options.get('side', 'guest')
