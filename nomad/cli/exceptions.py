class CLIError(Exception):
    """ An error occured during the processing of the CLI arguments. """

    def __init__(self, msg):
        self.msg = msg
