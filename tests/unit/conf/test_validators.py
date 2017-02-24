import pytest
from voluptuous.error import ValueInvalid

from lxdock.conf.validators import Hostname, LXDIdentifier


class TestHostnameValidator:
    def test_can_validate_a_basic_hostname(self):
        hostame_validator = Hostname('validator')
        assert hostame_validator('myhost')

    def test_can_validate_a_dotted_hostname(self):
        hostame_validator = Hostname('validator')
        assert hostame_validator('myhost.domain')

    def test_can_validate_a_dotted_hostname_ending_with_a_dot(self):
        hostame_validator = Hostname('validator')
        assert hostame_validator('myhost.domain.')

    def test_cannot_validate_a_hostname_taht_is_longer_than_255_characters(self):
        hostame_validator = Hostname('validator')
        with pytest.raises(ValueInvalid):
            hostame_validator('bad' * 100)


class TestLXDIdentifier:
    def test_can_validate_a_basic_identifier(self):
        id_validator = LXDIdentifier('validator')
        assert id_validator('myidentifier')

    def test_can_validate_identifiers_made_up_of_letters_digits_and_dashes(self):
        id_validator = LXDIdentifier('validator')
        assert id_validator('myidentifier01')
        assert id_validator('myidentifier-02-test')

    def test_cannot_allow_identifiers_that_do_not_start_with_letters(self):
        id_validator = LXDIdentifier('validator')
        with pytest.raises(ValueInvalid):
            id_validator('42identifier')

    def test_cannot_allow_identifiers_longer_than_63_characters(self):
        id_validator = LXDIdentifier('validator')
        assert id_validator('i' * 63)
        with pytest.raises(ValueInvalid):
            id_validator('i' * 64)
