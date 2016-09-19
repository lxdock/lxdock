from pathlib import Path
import argparse

import lxc

from .config import Config
from .provision import setup_debian_for_ansible, provision
from .util import add_share_to_container, run_cmd

WORK_CONTAINER_NAME = 'container'

class NeedsSuperuserError(Exception):
    pass

def get_parser():
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(dest='action')
    subparsers.add_parser('up')
    subparsers.add_parser('halt')
    subparsers.add_parser('provision')
    return parser

def get_workpath():
    workpath = Path('.vith').resolve()
    if not workpath.exists():
        workpath.mkdir()
    return workpath

def get_container():
    workpath = get_workpath()
    container = lxc.Container(WORK_CONTAINER_NAME, config_path=str(workpath))
    if not container.defined:
        print("Project container can't be opened. You should run vith as a superuser.")
        raise NeedsSuperuserError()
    return container

def action_up(args):
    confpath = Path('Vithfile.yml')
    conf = Config(confpath)
    workpath = get_workpath()
    containerpath = workpath / WORK_CONTAINER_NAME

    if not containerpath.exists():
        print("Cloning {} into local container...".format(conf['base_box']))
        base_container = lxc.Container(conf['base_box'])
        if not base_container.defined:
            print("Container {} does not exist. Maybe retry as a superuser?".format(conf['base_box']))
            return
        base_container.clone(newname=WORK_CONTAINER_NAME, config_path=str(workpath))

    container = get_container()
    if container.running:
        print("Container is already running!")
        return
    print("Starting container...")
    add_share_to_container(container, Path('.'), Path('vithshare'))
    container.start()
    if not container.running:
        print("Something went wrong trying to start the container.")
        return

    ips = container.get_ips(timeout=30)
    if not ips:
        print("There were problems trying to setup a network")
        return
    print("Started! IP: {}".format(', '.join(ips)))

def action_halt(args):
    container = get_container()
    if not container.running:
        print("The container is already stopped.")
        return
    print("Stopping...")
    if not container.shutdown(timeout=30):
        print("Something went wrong when trying to stop the container.")
    else:
        print("Stopped!")

def action_provision(args):
    confpath = Path('Vithfile.yml')
    conf = Config(confpath)
    container = get_container()
    if not container.running:
        print("The container is not running.")
        return

    print("Doing bare bone setup on the machine...")
    setup_debian_for_ansible(container)

    print("Provisioning container...")
    for provisioning_item in conf['provisioning']:
        print("Provisioning with {}".format(provisioning_item['type']))
        provision(container, provisioning_item)

def main():
    parser = get_parser()
    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        return
    action = {
        'up': action_up,
        'halt': action_halt,
        'provision': action_provision,
    }[args.action]
    try:
        action(args)
    except NeedsSuperuserError:
        print("Superuser powers needed.")

