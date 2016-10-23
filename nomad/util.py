from pathlib import Path

import pylxd

from .config import Config

class ContainerStatus:
    Stopped = 102
    Running = 103

def get_config():
    confpath = Path('.nomad.yml')
    return Config(confpath)

def get_client():
    return pylxd.Client()

def get_container(create=True):
    client = get_client()
    config = get_config()
    for container in client.containers.all():
        if container.config.get('user.nomad.homedir') == str(config.homedir):
            return container
    else:
        print("Can't find container for homedir %s" % config.homedir)
        if not create:
            return None

        allnames = {c.name for c in client.containers.all()}
        name = config['name']
        counter = 1
        while name in allnames:
            name = "%s%d" % (config['name'], counter)
            counter += 1

        print("Creating new container %s from image %s" % (name, config['image']))
        privileged = config.get('privileged', False)
        c = {
            'name': name,
            'source': {'type': 'image', 'alias': config['image']},
            'config': {
                'security.privileged': boolval(privileged),
                'user.nomad.homedir': str(config.homedir),
            },
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
    return container.config.get('user.nomad.provisioned') == 'true'

def has_static_ip(container):
    return container.config.get('user.nomad.static_ip') == 'true'
