"""
    Base utilities related to LXD and its settings
    ==============================================
    This module provides basic tools allowing to retrieve LXD settings / configuration options or to
    interract with LXD...
"""

import os


def get_lxd_dir():
    """ Returns the path (as a string) towards the LXD's directory. """
    return os.environ.get('LXD_DIR', None) or '/var/lib/lxd'
