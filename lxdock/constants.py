"""
    The ``constants`` module
    ========================

    This module defines top-level constants that can be used all tools or classes provided by
    LXDock, such as projects, containers or CLI parsers.

"""

from enum import Enum


# CONTAINER STATUSES
# --

CONTAINER_STOPPED = 102
CONTAINER_RUNNING = 103


# PROVISIONING
# --

class ProvisioningMode(Enum):
    """ Defines some common values that can be used to identify provisioning behavior types. """

    # In "auto" mode containers will be provisioned only at creation time.
    AUTO = 1

    # In "enabled" mode containers will be systematically provisioned.
    ENABLED = 2

    # In "disabled" mode containers won't be provisioned.
    DISABLED = 3
