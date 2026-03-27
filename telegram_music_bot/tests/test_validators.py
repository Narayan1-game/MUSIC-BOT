from bot.utils.validators import is_valid_url, validate_query


def test_validate_query():
    assert validate_query("hello") == "hello"


def test_validate_url_ssrf_block():
    assert not is_valid_url("http://127.0.0.1/test")
    assert is_valid_url("https://example.com")
