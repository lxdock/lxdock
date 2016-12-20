import io
import re
import subprocess
import tempfile


def get_ipv4_ip(container):
    """ Returns the IP adress of a specific container. """
    state = container.state()
    if state.network is None:  # container is not running
        return ''
    eth0 = state.network['eth0']
    for addr in eth0['addresses']:
        if addr['family'] == 'inet':
            return addr['address']
    return ''


def get_default_gateway(client):
    """ Given a PyLXD client, returns the default gateway of the associaited bridge. """
    lxdbr0 = client.networks.get('lxdbr0')
    cidr = lxdbr0.config['ipv4.address']
    return cidr.split('/')[0]


def get_used_ips(client):
    """ Returns the IP addresses that are already used by other containers. """
    result = []
    for c in client.containers.all():
        ip = get_ipv4_ip(c)
        if ip:
            result.append(ip)
    return result


def find_free_ip(client):
    """ Given a PyLXD client, returns a free IP address (and the related gateway). """
    gateway = get_default_gateway(client)
    prefix = '.'.join(gateway.split('.')[:-1])
    used_ips = set(get_used_ips(client))
    for i in range(1, 256):
        ip = '%s.%s' % (prefix, i)
        if ip != gateway and ip not in used_ips:
            return ip, gateway
    return None, None


RE_ETCHOST_LINE = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([\w\-_.]+)$')


class EtcHostsBase:
    def __init__(self, etchosts_fp):
        self.lines = etchosts_fp.readlines()
        self.changed = False
        self.nomad_bindings = {}
        self.nomad_section_begin = None
        self.nomad_section_end = None
        for i, line in enumerate(self.lines):
            if self.nomad_section_begin is None:
                if line.startswith('# BEGIN LXD-Nomad section'):
                    self.nomad_section_begin = i
            elif self.nomad_section_end is None:
                if line.startswith('# END LXD-Nomad section'):
                    self.nomad_section_end = i
                else:
                    m = RE_ETCHOST_LINE.match(line.strip())
                    if m:
                        self.nomad_bindings[m.group(2)] = m.group(1)
            else:
                break

    def ensure_binding_present(self, hostname, target_ip):
        if self.nomad_bindings.get(hostname) != target_ip:
            self.nomad_bindings[hostname] = target_ip
            self.changed = True

    def ensure_binding_absent(self, hostname):
        if hostname in self.nomad_bindings:
            del self.nomad_bindings[hostname]
            self.changed = True

    def get_mangled_contents(self):
        tosave = self.lines[:]
        if self.nomad_bindings:
            toinsert = ['# BEGIN LXD-Nomad section\n']
            toinsert += ['{} {}\n'.format(ip, host) for host, ip in self.nomad_bindings.items()]
            toinsert.append('# END LXD-Nomad section\n')
        else:
            toinsert = []
        if self.nomad_section_begin is not None:
            # Replace the current nomad section with our new hosts
            begin = self.nomad_section_begin
            end = self.nomad_section_end + 1 if self.nomad_section_end is not None else None
            tosave[begin:end] = toinsert
        else:
            # Append a new nomad section at the end of the file
            tosave += toinsert
        return tosave


class EtcHosts(EtcHostsBase):
    def __init__(self, path='/etc/hosts'):
        self.path = path
        etchosts_fp = open(self.path, 'rt', encoding='utf-8')
        super().__init__(etchosts_fp)

    def save(self):
        tosave = self.get_mangled_contents()
        with tempfile.NamedTemporaryFile('wt', encoding='utf-8') as fp:
            fp.writelines(tosave)
            fp.flush()
            cmd = "sudo cp {} {}".format(fp.name, self.path)
            p = subprocess.Popen(cmd, shell=True)
            p.wait()


class ContainerEtcHosts(EtcHostsBase):
    def __init__(self, container, path='/etc/hosts'):
        self.path = path
        self.container = container
        etchosts_contents = container.files.get(path).decode('utf-8')
        etchosts_fp = io.StringIO(etchosts_contents)
        super().__init__(etchosts_fp)

    def save(self):
        tosave = self.get_mangled_contents()
        towrite = ''.join(tosave).encode('utf-8')
        self.container.files.put(self.path, towrite)
