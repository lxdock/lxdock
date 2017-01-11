import os


def folderid(path):
    """ Computes a unique identifer using a folder path. """
    stats = os.stat(path)
    return str(stats.st_ino)
