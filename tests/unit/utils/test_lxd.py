from test.support import EnvironmentVarGuard

from lxdock.utils.lxd import get_lxd_dir


def test_get_lxd_helper_can_return_the_lxd_base_directory():
    env = EnvironmentVarGuard()
    with env:
        assert get_lxd_dir() == '/var/lib/lxd'
        env.set('LXD_DIR', '/my/test/lxd/')
        assert get_lxd_dir() == '/my/test/lxd/'
