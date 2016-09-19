from pathlib import Path

import lxc

def add_share_to_container(container, host_path, guest_path):
    host_path = host_path.resolve()
    if guest_path.is_absolute():
        # for some reason, guest path in mount entries don't have a leading /
        guest_path = guest_path.relative_to('/')
    rootfs = Path(container.get_config_item('lxc.rootfs'))
    guest_bind = rootfs / guest_path
    if not guest_bind.exists():
        guest_bind.mkdir(parents=True)
    entry_to_add = '{} {} none bind 0 0'.format(host_path, guest_path)
    mount_entries = container.get_config_item('lxc.mount.entry')
    if not entry_to_add in mount_entries:
        mount_entries.append(entry_to_add)
        container.set_config_item('lxc.mount.entry', mount_entries)

def run_cmd(container, cmd):
    return container.attach_wait(lxc.attach_run_command, cmd)

