class NomadException(Exception):
    def __init__(self, msg=None):
        self.msg = msg


class ProjectError(NomadException):
    """ An error occured while excuting some action at the project level. """


class ContainerOperationFailed(NomadException):
    """ An operation on a specific container failed. """
