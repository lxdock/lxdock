# -*- coding: utf-8 -*-


class ProjectError(Exception):
    """ An error occured while excuting some action at the project level. """

    def __init__(self, msg):
        self.msg = msg


class ContainerOperationFailed(Exception):
    """ An operation on a specific container failed. """
