import os

from lxdock.cli.project import get_project


FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


def test_get_project_function_can_return_a_valid_project_instance():
    homedir = os.path.join(FIXTURE_ROOT, 'project01')
    project = get_project(homedir)
    assert project.name == 'project01'
    assert project.homedir == homedir
