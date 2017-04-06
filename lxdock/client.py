import pylxd
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def get_client(**kwargs):
    """ Returns a PyLXD client to be used to orchestrate containers. """
    if 'verify' in kwargs and not kwargs['verify']:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    return pylxd.Client(**kwargs)
