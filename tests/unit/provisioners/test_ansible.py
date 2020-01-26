import re
import unittest.mock

import pytest

from lxdock.guests import AlpineGuest, DebianGuest
from lxdock.hosts import Host
from lxdock.provisioners import AnsibleProvisioner
from lxdock.test import FakeContainer


class TestAnsibleProvisioner:
    @pytest.mark.parametrize("options,expected_cmdargs", [
        ({}, ''),
        ({'vault_password_file': '.vpass'}, '--vault-password-file ./.vpass'),
        ({'ask_vault_pass': True}, '--ask-vault-pass'),
        ({'lxd_transport': True}, '-c lxd'),
    ])
    @unittest.mock.patch('subprocess.Popen')
    def test_can_run_ansible_playbooks(self, mock_popen, options, expected_cmdargs):
        host = Host()
        guest = DebianGuest(FakeContainer())
        lxd_state = unittest.mock.Mock()
        lxd_state.network.__getitem__ = unittest.mock.MagicMock(
            return_value={'addresses': [{'family': 'init', 'address': '0.0.0.0', }, ]})
        guest.lxd_container.state.return_value = lxd_state
        options['playbook'] = 'deploy.yml'
        provisioner = AnsibleProvisioner('./', host, [guest], options)
        provisioner.provision()
        m = re.match(
            r'ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --inventory-file /[/\w]+ '
            r'(.*)\s?./deploy.yml', mock_popen.call_args[0][0])
        assert m
        assert m.group(1).strip() == expected_cmdargs

    def test_can_properly_setup_ssh_for_alpine_guests(self):
        container = FakeContainer()
        lxd_container = container._container
        lxd_container.execute.return_value = ('ok', 'ok', '')
        host = Host()
        guest = AlpineGuest(container)
        provisioner = AnsibleProvisioner('./', host, [guest], {'playbook': 'deploy.yml'})
        provisioner.setup()
        EXPECTED = [
            ['apk', 'update'],
            ['apk', 'add'] + AnsibleProvisioner.guest_required_packages_alpine,
            ['apk', 'update'],
            ['apk', 'add', 'openssh'],
            ['rc-update', 'add', 'sshd'],
            ['/etc/init.d/sshd', 'start'],
            ['mkdir', '-p', '/root/.ssh'],
        ]
        calls = [tup[0][0] for tup in lxd_container.execute.call_args_list]
        assert calls == EXPECTED

    def test_inventory_contains_groups(self):
        c1 = FakeContainer(name='c1')
        c2 = FakeContainer(name='c2')
        # c3 is deliberately not part of our guests list. This is to test that it doesn't end up
        # in the inventory and result in spurious unreachable hosts. These situations can happen
        # in two ways: errors in the config file, or guest filtering in the command line ("lxdock
        # provision c1, c2" for example).
        provisioner = AnsibleProvisioner(
            './',
            Host(),
            [DebianGuest(c1), DebianGuest(c2)],
            {'playbook': 'deploy.yml', 'groups': {'g1': ['c1', 'c2'], 'g2': ['c1', 'c3']}}
        )
        inv = provisioner.get_inventory()
        # group order is not guaranteed. our tests have to be written with that in mind.
        groups = re.findall(r'\[(g1|g2)\]([^[]+)', inv, re.MULTILINE)
        # we sort so that g1 will be first all the time
        groups = sorted([(gname, hosts.strip()) for gname, hosts in groups])
        assert sorted(groups) == [('g1', 'c1\nc2'), ('g2', 'c1')]

    def test_inventory_with_lxd_transport(self):
        c = FakeContainer(name='c1')
        provisioner = AnsibleProvisioner(
            './',
            Host(),
            [DebianGuest(c)],
            {'playbook': 'deploy.yml', 'lxd_transport': True}
        )
        inv = provisioner.get_inventory()
        assert 'ansible_host={}'.format(c.lxd_name) in inv
