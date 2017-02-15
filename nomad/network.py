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


def get_used_ips(client):
    """ Returns the IP addresses that are already used by other containers. """
    result = []
    for c in client.containers.all():
        ip = get_ipv4_ip(c)
        if ip:
            result.append(ip)
    return result


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
        # First, let's try to write the file directly. Who knows, it might work!
        try:
            with open(self.path, 'wt', encoding='utf-8') as fp:
                fp.writelines(tosave)
        except PermissionError:
            # Ok, we don't have permission to /etc/hosts. Let's save it to a temp file and
            # "sudo cp" it to /etc/hosts
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
