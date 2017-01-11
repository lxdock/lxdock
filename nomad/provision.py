import logging
import os.path
import subprocess
import tempfile
from pathlib import Path

from .network import get_ipv4_ip
from .utils.container import run_cmd

logger = logging.getLogger(__name__)


def prepare_debian(container):
    packages = [
        'apt-utils',
        'aptitude',
        'openssh-server',
        'python',
    ]
    pubkey_path = Path(os.path.expanduser('~/.ssh/id_rsa.pub'))
    pubkey = pubkey_path.open().read()
    run_cmd(container, ['apt-get', 'install', '-y'] + packages)
    run_cmd(container, ['mkdir', '-p', '/root/.ssh'])
    logger.info("Adding %s to machine's authorized keys" % pubkey)
    container.files.put('/root/.ssh/authorized_keys', pubkey)


def set_static_ip_on_debian(container, ip, gateway):
    contents = """
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
\taddress {ip}
\tnetmask 255.255.255.0
\tgateway {gateway}
""".format(ip=ip, gateway=gateway)
    container.files.put('/etc/network/interfaces', contents)
    resolvconf = "nameserver %s" % gateway
    container.files.put('/etc/resolv.conf', resolvconf)


def provision_with_ansible(container, provisioning_item):
    assert provisioning_item['type'] == 'ansible'
    ip = get_ipv4_ip(container)
    with tempfile.NamedTemporaryFile() as tmpinv:
        tmpinv.write("{} ansible_user=root".format(ip).encode('ascii'))
        tmpinv.flush()
        cmd = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i {} {}".format(
            tmpinv.name, provisioning_item['playbook'])
        logger.debug(cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
