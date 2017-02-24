import logging
import subprocess
import tempfile

from ..network import get_ipv4_ip

from .base import Provisioner

logger = logging.getLogger(__name__)


class AnsibleProvisioner(Provisioner):
    """ Allows to perform provisioning operations using Ansible. """

    name = 'ansible'

    def provision(self):
        """ Performs the provisioning operations using the considered provisioner. """
        ip = get_ipv4_ip(self.lxd_container)
        with tempfile.NamedTemporaryFile() as tmpinv:
            tmpinv.write('{} ansible_user=root'.format(ip).encode('ascii'))
            tmpinv.flush()
            cmd = 'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i {} {}'.format(
                tmpinv.name, self.options['playbook'])
            logger.debug(cmd)
            p = subprocess.Popen(cmd, shell=True)
            p.wait()
