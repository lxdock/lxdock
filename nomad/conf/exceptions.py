class ConfigError(Exception):
    """ An error related to the configuration of the Nomad project occured. """

    def __init__(self, msg):
        self.msg = msg


class ConfigFileNotFoundError(ConfigError):
    """ The LXD-Nomad config file was not found. """


class ConfigFileValidationError(ConfigError):
    """ The LXD-Nomad config file was not valid. """
