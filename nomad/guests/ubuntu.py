from .debian import DebianGuest


class UbuntuGuest(DebianGuest):
    """ This guest can provision Ubuntu containers. """

    name = 'ubuntu'
