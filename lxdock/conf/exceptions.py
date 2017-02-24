class ConfigError(Exception):
    """ An error related to the configuration of the LXDock project occured. """

    def __init__(self, msg):
        self.msg = msg


class ConfigFileNotFoundError(ConfigError):
    """ The LXDock config file was not found. """


class ConfigFileValidationError(ConfigError):
    """ The LXDock config file was not valid. """
