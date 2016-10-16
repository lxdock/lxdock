class ContainerStatus:
    Stopped = 102
    Running = 103

def run_cmd(container, cmd):
    print("Running %s" % (' '.join(cmd)))
    stdout, stderr = container.execute(cmd)
    print(stdout)
    print(stderr)

def get_ipv4_ip(container):
    state = container.state()
    eth0 = state.network['eth0']
    for addr in eth0['addresses']:
        if addr['family'] == 'inet':
            return addr['address']
    return ''
