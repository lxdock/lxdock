from pathlib import Path

from .util import run_cmd

def setup_debian_for_ansible(container):
    packages = [
        'python-dev',
        'python-setuptools',
        'python-pip',
        'libffi-dev',
        'libssl-dev',
        'python-apt',
        'aptitude',
    ]
    run_cmd(container, ['apt-get', 'install', '-y'] + packages)
    run_cmd(container, ['pip', 'install', '-U', 'setuptools'])
    run_cmd(container, ['pip', 'install', 'ansible'])

    def write_ansible_inventory():
        p = Path('/etc/ansible/hosts')
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with p.open('w') as fp:
            fp.write('127.0.0.1\n')

    container.attach_wait(write_ansible_inventory)

def provision(container, provisioning_item):
    assert provisioning_item['type'] == 'ansible'
    playbook_path = Path('/vithshare') / provisioning_item['playbook']
    run_cmd(container, ['ansible-playbook', '--connection=local', str(playbook_path)])

