import pytest

from bot.utils.validators import ValidationError, validate_query, validate_url


def test_validate_query_ok():
    assert validate_query('hello') == 'hello'


def test_validate_query_bad():
    with pytest.raises(ValidationError):
        validate_query('')


def test_validate_url_scheme():
    with pytest.raises(ValidationError):
        validate_url('ftp://example.com')
