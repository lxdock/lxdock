import os.path
from pathlib import Path
import tempfile
import subprocess

from .util import run_cmd, get_ipv4_ip

def setup_ssh_access_on_debian(container):
    packages = [
        'openssh-server',
    ]
    pubkey_path = Path(os.path.expanduser('~/.ssh/id_rsa.pub'))
    pubkey = pubkey_path.open().read()
    run_cmd(container, ['apt-get', 'install', '-y'] + packages)
    run_cmd(container, ['mkdir', '-p', '/root/.ssh'])
    print("Adding %s to machine's authorized keys" % pubkey)
    container.files.put('/root/.ssh/authorized_keys', pubkey)

def provision(container, provisioning_item):
    assert provisioning_item['type'] == 'ansible'
    ip = get_ipv4_ip(container)
    with tempfile.NamedTemporaryFile() as tmpinv:
        tmpinv.write("{} ansible_user=root host_key_checking=False".format(ip).encode('ascii'))
        tmpinv.flush()
        print(['ansible-playbook', '-i', tmpinv.name, provisioning_item['playbook']])
        subprocess.call(['ansible-playbook', '-i', tmpinv.name, provisioning_item['playbook']])

