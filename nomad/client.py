import pylxd


def get_client():
    """ Returns a PyLXD client to be used to orchestrate containers. """
    return pylxd.Client()
