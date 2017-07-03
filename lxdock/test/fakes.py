from unittest.mock import Mock

from ..container import Container


class FakeContainer(Container):
    def __init__(self, project_name='project', homedir='/foo', client=None, **options):
        if client is None:
            client = Mock()
        options.setdefault('name', 'fakecontainer')
        super().__init__(project_name, homedir, client, **options)

    def _get_container(self, create=True):
        result = Mock()
        result.execute.return_value = ('ok', 'ok', '')
        return result
