import re

from voluptuous.schema_builder import message
from voluptuous.validators import truth


hostname_part_re = re.compile(r'(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
lxd_identifier_re = re.compile(r'^(([A-Z]|[A-Z][A-Z0-9\-]*[A-Z0-9])\.)*([A-Z]|[A-Z][A-Z0-9\-]*[A-Z0-9])$', re.IGNORECASE)  # noqa


@message('expected a valid hostname')
@truth
def Hostname(v):
    """ Validates a hostname. """
    if len(v) > 255:
        return False
    # Strips one dot from the right if applicable.
    v = v[:-1] if v.endswith('.') else v
    # Validates each part of the hostname.
    return all(hostname_part_re.match(part) for part in v.split('.'))


@message(
    'expected a valid identifer no longer than 63 characters, starting with letters and made up of '
    'letters, digits and dashes')
@truth
def LXDIdentifier(v):
    """ Validates an identifier that should obey to the same rules as RFC 952 hostnames. """
    if len(v) > 63:
        return False
    return lxd_identifier_re.match(v)
