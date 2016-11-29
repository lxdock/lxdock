# -*- coding: utf-8 -*-

import argparse
import logging
import sys

from .. import __version__

from .project import get_project

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


class Nomad(object):
    """ Wrapper around  the LXD-Nomad argument parser and the related actions. """

    def __init__(self):
        # Create the argument parsers
        parser = argparse.ArgumentParser(
            description='Orchestrate and run multiple containers using LXD.', prog='LXD-Nomad')
        parser.add_argument(
            '--version', action='version', version='%(prog)s {v}'.format(v=__version__))
        parser.add_argument('-v', '--verbose', action='store_true')
        subparsers = parser.add_subparsers(dest='action')
        subparsers.add_parser('destroy', help='Stop and remove containers.')
        subparsers.add_parser('halt', help='Stop containers.')
        subparsers.add_parser('provision', help='Provision containers.')
        subparsers.add_parser('shell', help='Opens a shell in the container.')
        subparsers.add_parser('up', help='Create, start and provisions containers.')

        # Parses the arguments
        args = parser.parse_args()

        # Handles verbosity
        if args.verbose:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)

        # Initializes the LXD-Nomad project
        self.project = get_project()

        # use dispatch pattern to invoke method with same name
        getattr(self, args.action)(args)

    def destroy(self, args):
        self.project.destroy()

    def halt(self, args):
        self.project.halt()

    def provision(self, args):
        self.project.provision()

    def shell(self, args):
        self.project.shell()

    def up(self, args):
        self.project.up()


def main():
    # Setup logging
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)
    # Disables requests logging
    logging.getLogger('requests').propagate = False

    # Run the Nomad orchestration tool!
    Nomad()
