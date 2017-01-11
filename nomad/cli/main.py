import argparse
import logging
import sys

from .. import __version__
from ..conf.exceptions import ConfigError
from ..exceptions import ProjectError
from ..logging import console_handler

from .exceptions import CLIError
from .project import get_project

logger = logging.getLogger(__name__)


class Nomad(object):
    """ Wrapper around  the LXD-Nomad argument parser and the related actions. """

    def __init__(self):
        self._parsers = {}

        # Creates the argument parsers
        parser = argparse.ArgumentParser(
            description='Orchestrate and run multiple containers using LXD.', prog='LXD-Nomad')
        parser.add_argument(
            '--version', action='version', version='%(prog)s {v}'.format(v=__version__))
        parser.add_argument('-v', '--verbose', action='store_true')
        self._parsers['main'] = parser

        subparsers = parser.add_subparsers(dest='action')

        # Creates the 'destroy' action.
        self._parsers['destroy'] = subparsers.add_parser(
            'destroy', help='Stop and remove containers.')

        # Creates the 'halt' action.
        self._parsers['halt'] = subparsers.add_parser('halt', help='Stop containers.')

        # Creates the 'help' action.
        self._parsers['help'] = subparsers.add_parser('help', help='Show help information.')
        self._parsers['help'].add_argument('subcommand', nargs='?', help='Subcommand name.')

        # Creates the 'provision' action.
        self._parsers['provision'] = subparsers.add_parser(
            'provision', help='Provision containers.')

        # Creates the 'shell' action.
        self._parsers['shell'] = subparsers.add_parser(
            'shell', help='Open a shell in the container.')

        # Creates the 'up' action.
        self._parsers['up'] = subparsers.add_parser(
            'up', help='Create, start and provision containers.')

        # Add common arguments to the action parsers that can be used with a specific container.
        per_container_parsers = ['destroy', 'halt', 'provision', 'shell', 'up', ]
        for pkey in per_container_parsers:
            self._parsers[pkey].add_argument('name', nargs='?', help='Container name.')

        # Parses the arguments
        args = parser.parse_args()

        # Displays the help if no action is specified
        if args.action is None:
            parser.print_help()
            sys.exit(1)

        # Handles verbosity
        if args.verbose:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)

        try:
            # use dispatch pattern to invoke method with same name
            getattr(self, args.action)(args)
        except (CLIError, ConfigError, ProjectError) as e:
            logger.error(e.msg)
            sys.exit(1)

    def destroy(self, args):
        self.project.destroy(container_name=args.name)

    def halt(self, args):
        self.project.halt(container_name=args.name)

    def help(self, args):
        try:
            assert args.subcommand is not None
            self._parsers[args.subcommand].print_help()
        except AssertionError:
            self._parsers['main'].print_help()
        except KeyError:
            # args.subcommand is not a valid subcommand!
            raise CLIError('No such command: {}'.format(args.subcommand))

    def provision(self, args):
        self.project.provision(container_name=args.name)

    def shell(self, args):
        self.project.shell(container_name=args.name)

    def up(self, args):
        self.project.up(container_name=args.name)

    ##################################
    # UTILITY METHODS AND PROPERTIES #
    ##################################

    @property
    def project(self):
        """ Initializes a LXD-Nomad project instance and returns it. """
        if not hasattr(self, '_project'):
            self._project = get_project()
        return self._project


def main():
    # Setup logging
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)
    # Disables requests logging
    logging.getLogger('requests').propagate = False
    logging.getLogger('ws4py').propagate = False

    # Run the Nomad orchestration tool!
    Nomad()
