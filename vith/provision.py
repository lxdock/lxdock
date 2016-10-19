import os.path
from pathlib import Path
import tempfile
import subprocess

from .util import run_cmd, get_ipv4_ip

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
    print("Adding %s to machine's authorized keys" % pubkey)
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
    run_cmd(container, ['/etc/init.d/networking', 'stop'])
    run_cmd(container, ['/etc/init.d/networking', 'start'])

def provision(container, provisioning_item):
    assert provisioning_item['type'] == 'ansible'
    ip = get_ipv4_ip(container)
    with tempfile.NamedTemporaryFile() as tmpinv:
        tmpinv.write("{} ansible_user=root".format(ip).encode('ascii'))
        tmpinv.flush()
        cmd = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i {} {}".format(tmpinv.name, provisioning_item['playbook'])
        print(cmd)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()

