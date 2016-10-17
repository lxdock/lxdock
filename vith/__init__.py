import argparse

import pylxd

from .provision import prepare_debian, provision, set_static_ip_on_debian
from .util import (
    ContainerStatus, get_ipv4_ip, get_config, get_client, get_default_gateway, find_free_ip,
    wait_for_ipv4_ip
)


def get_parser():
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(dest='action')
    subparsers.add_parser('up')
    subparsers.add_parser('halt')
    subparsers.add_parser('provision')
    subparsers.add_parser('destroy')
    return parser

def get_container(create=True):
    client = get_client()
    config = get_config()
    try:
        return client.containers.get(config['name'])
    except pylxd.exceptions.LXDAPIException as e:
        print("Can't get container: %s" % e)
        if not create:
            return None
        print("Creating new container from image %s" % config['image'])
        c = {
            'name': config['name'],
            'source': {'type': 'image', 'alias': config['image']}
        }
        try:
            return client.containers.create(c, wait=True)
        except pylxd.exceptions.LXDAPIException as e:
            print("Can't create container: %s" % e)
            raise

def action_up(args):
    container = get_container()
    if container.status_code == ContainerStatus.Running:
        print("Container is already running!")
        return
    print("Starting container...")
    container.start(wait=True)
    if container.status_code != ContainerStatus.Running:
        print("Something went wrong trying to start the container.")
        return
    ip = get_ipv4_ip(container)
    if not ip:
        print("No IP yet, waiting 10 seconds...")
        ip = wait_for_ipv4_ip(container)
    if not ip:
        print("Still no IP! Forcing a static IP...")
        gateway = get_default_gateway()
        forced_ip = find_free_ip(gateway)
        set_static_ip_on_debian(container, forced_ip, gateway)
        ip = wait_for_ipv4_ip(container)
    if ip:
        print("Container is up! IP: %s" % ip)
    else:
        print("STILL no IP! Container is up, but probably broken.")

def action_halt(args):
    container = get_container()
    if container.status_code == ContainerStatus.Stopped:
        print("The container is already stopped.")
        return
    print("Stopping...")
    try:
        container.stop(timeout=30, force=False, wait=True)
    except pylxd.exceptions.LXDAPIException:
        print("Can't stop the container. Forcing...")
        container.stop(force=True, wait=True)

def action_provision(args):
    config = get_config()
    container = get_container()
    if container.status_code != ContainerStatus.Running:
        print("The container is not running.")
        return

    print("Doing bare bone setup on the machine...")
    prepare_debian(container)

    print("Provisioning container...")
    for provisioning_item in config['provisioning']:
        print("Provisioning with {}".format(provisioning_item['type']))
        provision(container, provisioning_item)

def action_destroy(args):
    container = get_container(create=False)
    if container is None:
        print("Container doesn't exist, nothing to destroy.")
        return

    action_halt(args)
    container = get_container()
    print("Destroying...")
    container.delete(wait=True)
    print("Destroyed!")

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
        'destroy': action_destroy,
    }[args.action]
    action(args)

