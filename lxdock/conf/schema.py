from voluptuous import ALLOW_EXTRA, All, Any, Coerce, Extra, In, Length, Required, Schema, Url

from ..provisioners import Provisioner
from .validators import ExpandUserIfExists, Hostname, LXDIdentifier


def get_schema():
    _top_level_and_containers_common_options = {
        'environment': {Extra: Coerce(str)},
        'hostnames': [Hostname(), ],
        'image': str,
        'lxc_config': {Extra: str},
        'mode': In(['local', 'pull', ]),
        'privileged': bool,
        'profiles': [str, ],
        'protocol': In(['lxd', 'simplestreams', ]),
        'provisioning': [],  # will be set dynamically using provisioner classes...
        'server': Url(),
        'shares': [{
            'source': ExpandUserIfExists,
            'dest': str,
            'set_host_acl': bool,  # TODO: need a way to deprecate this
            'share_properties': {Extra: Coerce(str)},
        }],
        'shell': {
            'user': str,
            'home': str,  # TODO: deprecated
        },
        'users': [{
            # Usernames max length is set 32 characters according to useradd's man page.
            Required('name'): All(str, Length(max=32)),
            'home': str,
            'password': str,
            'shell': str,
        }],
        'extras': {
            'network_wait_timeout': int
        }
    }

    def _check_provisioner_config(config):
        provisioners = Provisioner.provisioners.values()

        # Check if 'type' is correctly defined
        Schema({Required('type'): Any(*[provisioner.name for provisioner in provisioners])},
               extra=ALLOW_EXTRA)(config)

        # Check if the detected provisioner's schema is fully satisfied
        c = config.copy()
        name = c.pop('type')
        detected_provisioner = next(provisioner for provisioner in provisioners
                                    if provisioner.name == name)
        validated = Schema(detected_provisioner.schema)(c)
        validated['type'] = name
        return validated

    # Inserts provisioner specific schema rules in the global schema dict.
    _top_level_and_containers_common_options['provisioning'] = [All(_check_provisioner_config)]

    _container_options = {
        Required('name'): LXDIdentifier(),
    }
    _container_options.update(_top_level_and_containers_common_options)

    _lxdock_options = {
        Required('name'): LXDIdentifier(),
        'containers': [_container_options, ],
    }
    _lxdock_options.update(_top_level_and_containers_common_options)

    return Schema(_lxdock_options)


# The schema will be used to validate LXDock files!
schema = get_schema()
