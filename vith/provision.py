import lxc

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
    cmd = ['apt-get', 'install', '-y'] + packages
    container.attach_wait(lxc.attach_run_command, cmd)
    cmd = ['pip', 'install', '-U', 'setuptools']
    container.attach_wait(lxc.attach_run_command, cmd)
    cmd = ['pip', 'install', 'ansible']
    container.attach_wait(lxc.attach_run_command, cmd)

def provision(container, config):
    pass
