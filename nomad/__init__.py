import argparse

from . import action

def get_parser():
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(dest='action')
    subparsers.add_parser('up')
    subparsers.add_parser('halt')
    subparsers.add_parser('provision')
    subparsers.add_parser('destroy')
    return parser

def action_up(args):
    action.up()

def action_halt(args):
    action.halt()

def action_provision(args):
    action.provision()

def action_destroy(args):
    action.destroy()

def main():
    parser = get_parser()
    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        return
    action_func = {
        'up': action_up,
        'halt': action_halt,
        'provision': action_provision,
        'destroy': action_destroy,
    }[args.action]
    action_func(args)

