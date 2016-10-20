from pathlib import Path
import time

import pylxd

from .config import Config

class ContainerStatus:
    Stopped = 102
    Running = 103

def get_config():
    confpath = Path('Vithfile.yml')
    return Config(confpath)

def get_client():
    return pylxd.Client()

def get_container(create=True):
    client = get_client()
    config = get_config()
    try:
        return client.containers.get(config['name'])
    except pylxd.exceptions.LXDAPIException as e:
        print("Can't get container: %s" % e)
        if not create:
            return None
        print("Creating new container from image %s" % config['image'])
        privileged = config.get('privileged', False)
        c = {
            'name': config['name'],
            'source': {'type': 'image', 'alias': config['image']},
            'config': {'security.privileged': boolval(privileged)},
        }
        try:
            return client.containers.create(c, wait=True)
        except pylxd.exceptions.LXDAPIException as e:
            print("Can't create container: %s" % e)
            raise

def run_cmd(container, cmd):
    print("Running %s" % (' '.join(cmd)))
    stdout, stderr = container.execute(cmd)
    print(stdout)
    print(stderr)

def get_ipv4_ip(container):
    state = container.state()
    if state.network is None: # container is not running
        return ''
    eth0 = state.network['eth0']
    for addr in eth0['addresses']:
        if addr['family'] == 'inet':
            return addr['address']
    return ''

def wait_for_ipv4_ip(container, seconds=10):
    for i in range(seconds):
        time.sleep(1)
        ip = get_ipv4_ip(container)
        if ip:
            return ip
    return ''

def get_default_gateway():
    client = get_client()
    lxdbr0 = client.networks.get('lxdbr0')
    cidr = lxdbr0.config['ipv4.address']
    return cidr.split('/')[0]

def get_used_ips():
    client = get_client()
    result = []
    for c in client.containers.all():
        ip = get_ipv4_ip(c)
        if ip:
            result.append(ip)
    return result

def find_free_ip(gateway):
    prefix = '.'.join(gateway.split('.')[:-1])
    used_ips = set(get_used_ips())
    for i in range(1, 256):
        ip = '%s.%s' % (prefix, i)
        if ip != gateway and ip not in used_ips:
            return ip
    return None

def boolval(val):
    return 'true' if val else 'false'

def is_provisioned(container):
    return container.config.get('user.vith.provisioned') == 'true'

