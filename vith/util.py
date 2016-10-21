from pathlib import Path

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

def boolval(val):
    return 'true' if val else 'false'

def is_provisioned(container):
    return container.config.get('user.vith.provisioned') == 'true'

