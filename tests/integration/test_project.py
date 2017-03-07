import os
import unittest.mock

import pytest

from lxdock.conf.config import Config
from lxdock.container import Container
from lxdock.exceptions import ProjectError
from lxdock.project import Project
from lxdock.test import LXDTestCase


THIS_DIR = os.path.join(os.path.dirname(__file__))
FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestProject(LXDTestCase):
    def test_can_be_initialized_from_a_config_file(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project01')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project01', homedir, self.client, config)
        assert project.name == 'project01'
        assert project.homedir == homedir
        assert len(project.containers) == 1
        assert project.containers[0].name == 'default'
        assert project.containers[0].homedir == homedir
        assert project.containers[0].options['mode'] == 'pull'
        assert project.containers[0].options['image'] == 'ubuntu/xenial'

    def test_can_return_a_container_by_name(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project02')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        container = project.get_container_by_name('lxdock-pytest-web')
        assert container and container.name == 'lxdock-pytest-web'

    def test_raises_an_error_if_it_cannot_find_a_container(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project02')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        with pytest.raises(ProjectError):
            project.get_container_by_name('dummy')

    def test_can_start_all_the_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project03')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        project.up()
        for container in project.containers:
            assert container.is_running

    def test_can_start_some_specific_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project02')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        project.up(container_names=['lxdock-pytest-web'])
        container_web = project.get_container_by_name('lxdock-pytest-web')
        container_ci = project.get_container_by_name('lxdock-pytest-ci')
        assert container_web.is_running
        assert container_ci.is_stopped

    def test_can_halt_all_the_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project03')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        project.up()
        project.halt()
        for container in project.containers:
            assert container.is_stopped

    def test_can_halt_some_specific_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project02')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        project.up()
        project.halt(container_names=['lxdock-pytest-web'])
        container_web = project.get_container_by_name('lxdock-pytest-web')
        container_ci = project.get_container_by_name('lxdock-pytest-ci')
        assert container_web.is_stopped
        assert container_ci.is_running

    def test_can_provision_all_the_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project03')
        container_options = {
            'name': self.containername('dummytest'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'provisioning': [
                {'type': 'ansible',
                 'playbook': os.path.join(THIS_DIR, 'fixtures/provision_with_ansible.yml'), }
            ],
        }
        project = Project(
            'project02', homedir, self.client,
            [Container('myproject', THIS_DIR, self.client, **container_options)])
        project.up()
        project.provision()
        for container in project.containers:
            assert container.is_provisioned

    def test_can_provision_some_specific_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project03')
        container_options = {
            'name': self.containername('thisisatest'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'provisioning': [
                {'type': 'ansible',
                 'playbook': os.path.join(THIS_DIR, 'fixtures/provision_with_ansible.yml'), }
            ],
        }
        project = Project(
            'project02', homedir, self.client,
            [Container('myproject', THIS_DIR, self.client, **container_options)])
        project.up()
        project.provision(container_names=['lxdock-pytest-thisisatest'])
        container_web = project.get_container_by_name('lxdock-pytest-thisisatest')
        assert container_web.is_provisioned

    def test_can_destroy_all_the_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project03')
        container_options = {
            'name': self.containername('dummytest'), 'image': 'ubuntu/xenial', 'mode': 'pull',
            'provisioning': [
                {'type': 'ansible',
                 'playbook': os.path.join(THIS_DIR, 'fixtures/provision_with_ansible.yml'), }
            ],
        }
        project = Project(
            'project02', homedir, self.client,
            [Container('myproject', THIS_DIR, self.client, **container_options)])
        project.up()
        project.destroy()
        for container in project.containers:
            assert not container.exists

    def test_can_destroy_some_specific_containers_of_a_project(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project02')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        project.up()
        project.destroy(container_names=['lxdock-pytest-web'])
        container_web = project.get_container_by_name('lxdock-pytest-web')
        container_ci = project.get_container_by_name('lxdock-pytest-ci')
        assert not container_web.exists
        assert container_ci.exists

    def test_cannot_open_shell_into_many_containers(self):
        homedir = os.path.join(FIXTURE_ROOT, 'project02')
        config = Config.from_base_dir(homedir)
        project = Project.from_config('project02', homedir, self.client, config)
        with pytest.raises(ProjectError):
            project.shell()

    @unittest.mock.patch('subprocess.call')
    def test_can_open_a_shell_for_a_specific_container(self, mocked_call, persistent_container):
        homedir = os.path.join(FIXTURE_ROOT, 'project03')
        project = Project('project02', homedir, self.client, [persistent_container, ])
        project.shell(container_name='testcase-persistent')
        assert mocked_call.call_count == 1
        assert mocked_call.call_args[0][0] == \
            'lxc exec {} -- su -m root'.format(persistent_container.lxd_name)
