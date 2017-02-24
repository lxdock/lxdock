import unittest.mock

from lxdock.cli.utils import yesno


class TestYesNoFunction(object):
    def test_can_accept_yes_answers(self):
        with unittest.mock.patch('builtins.input', return_value='Y'):
            assert yesno('True or False?')
        with unittest.mock.patch('builtins.input', return_value='y'):
            assert yesno('True or False?')
        with unittest.mock.patch('builtins.input', return_value='Yes'):
            assert yesno('True or False?')
        with unittest.mock.patch('builtins.input', return_value='yes'):
            assert yesno('True or False?')

    def test_can_accept_no_answers(self):
        with unittest.mock.patch('builtins.input', return_value='N'):
            assert not yesno('True or False?')
        with unittest.mock.patch('builtins.input', return_value='n'):
            assert not yesno('True or False?')
        with unittest.mock.patch('builtins.input', return_value='No'):
            assert not yesno('True or False?')
        with unittest.mock.patch('builtins.input', return_value='no'):
            assert not yesno('True or False?')
