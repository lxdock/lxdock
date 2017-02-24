from voluptuous import All, In, IsDir, Length, Required, Schema, Url

from .validators import Hostname, LXDIdentifier


_top_level_and_containers_common_options = {
    'hostnames': [Hostname(), ],
    'image': str,
    'mode': In(['local', 'pull', ]),
    'privileged': bool,
    'protocol': In(['lxd', 'simplestreams', ]),
    'provisioning': [{
        # Common options
        'type': str,

        # Ansible specific options
        'playbook': str,
    }],
    'server': Url(),
    'shares': [{
        # The existence of the source directory will be checked!
        'source': IsDir(),
        'dest': str,
    }],
    'shell': {
        'user': str,
        'home': str,
    },
    'users': [{
        # Usernames max length is set 32 characters according to useradd's man page.
        Required('name'): All(str, Length(max=32)),
        'home': str,
    }],
}

_container_options = {
    Required('name'): LXDIdentifier(),
}
_container_options.update(_top_level_and_containers_common_options)

_lxdock_options = {
    Required('name'): LXDIdentifier(),
    'containers': [_container_options, ],
}
_lxdock_options.update(_top_level_and_containers_common_options)

# The schema will be used to validate LXDock files!
schema = Schema(_lxdock_options)
