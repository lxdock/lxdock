# -*- coding: utf-8 -*-

import argparse
import logging
import sys

from .. import __version__
from ..exceptions import ProjectError
from ..logging import console_handler

from .project import get_project

logger = logging.getLogger(__name__)


class Nomad(object):
    """ Wrapper around  the LXD-Nomad argument parser and the related actions. """

    def __init__(self):
        # Creates the argument parsers
        parser = argparse.ArgumentParser(
            description='Orchestrate and run multiple containers using LXD.', prog='LXD-Nomad')
        parser.add_argument(
            '--version', action='version', version='%(prog)s {v}'.format(v=__version__))
        parser.add_argument('-v', '--verbose', action='store_true')
        subparsers = parser.add_subparsers(dest='action')

        # Creates the 'destroy' action.
        destroy_parser = subparsers.add_parser('destroy', help='Stop and remove containers.')

        # Creates the 'halt' action.
        halt_parser = subparsers.add_parser('halt', help='Stop containers.')

        # Creates the 'provision' action.
        provision_parser = subparsers.add_parser('provision', help='Provision containers.')

        # Creates the 'shell' action.
        shell_parser = subparsers.add_parser('shell', help='Open a shell in the container.')

        # Creates the 'up' action.
        up_parser = subparsers.add_parser('up', help='Create, start and provisions containers.')

        # Add common arguments to the action parsers that can be used with a specific container.
        per_container_parsers = [
            destroy_parser, halt_parser, provision_parser, shell_parser, up_parser, ]
        for p in per_container_parsers:
            p.add_argument('name', nargs='?', help='Container name.')

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

        # Initializes the LXD-Nomad project
        self.project = get_project()

        try:
            # use dispatch pattern to invoke method with same name
            getattr(self, args.action)(args)
        except ProjectError as e:
            logger.error(e.msg)

    def destroy(self, args):
        self.project.destroy(container_name=args.name)

    def halt(self, args):
        self.project.halt(container_name=args.name)

    def provision(self, args):
        self.project.provision(container_name=args.name)

    def shell(self, args):
        self.project.shell(container_name=args.name)

    def up(self, args):
        self.project.up(container_name=args.name)


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
