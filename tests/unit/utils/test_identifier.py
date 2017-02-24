import os

from lxdock.utils.identifier import folderid


def test_folderid_helper_returns_an_identifier_based_on_inode_numbers():
    path = '.'
    stats = os.stat(path)
    assert str(stats.st_ino) in folderid(path)
