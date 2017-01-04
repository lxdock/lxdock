# -*- coding: utf-8 -*-

import os


def folderid(path):
    """ Computes a unique identifer using a folder path. """
    stats = os.stat(path)
    return '{dev}{ino}'.format(dev=stats.st_dev, ino=stats.st_ino)
