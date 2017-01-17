import logging
import sys

from colorlog import ColoredFormatter

LOG_COLORS = {
    'DEBUG':    'reset',
    'INFO':     'reset',
    'WARNING':  'yellow',
    'ERROR':    'bold_red,bg_white',
    'CRITICAL': 'bold_red,bg_white',
}


def get_default_formatter():
    """ Returns the default formatter used to log messages for nomad. """
    return ColoredFormatter('%(log_color)s%(message)s', log_colors=LOG_COLORS)


def get_per_container_formatter(container_name):
    """ Returns a logging formatter which prefixes each message with a container name. """
    return ColoredFormatter(
        '%(log_color)s==> {name}: %(message)s'.format(name=container_name), log_colors=LOG_COLORS)


logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setFormatter(get_default_formatter())
