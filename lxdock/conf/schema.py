from voluptuous import All, Any, Coerce, Extra, In, IsDir, Length, Required, Schema, Url

from ..provisioners import Provisioner

from .validators import Hostname, LXDIdentifier


_top_level_and_containers_common_options = {
    'environment': {Extra: Coerce(str)},
    'hostnames': [Hostname(), ],
    'image': str,
    'mode': In(['local', 'pull', ]),
    'privileged': bool,
    'protocol': In(['lxd', 'simplestreams', ]),
    'provisioning': [],  # will be set dynamically using provisioner classes...
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
        'password': str,
    }],
}

# Inserts provisioner specific schema rules in the global schema dict.
_top_level_and_containers_common_options['provisioning'] = [
    Any(*[dict([(Required('type'), provisioner.name), ] + list(provisioner.schema.items()))
          for provisioner in Provisioner.provisioners.values()]),
]

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
