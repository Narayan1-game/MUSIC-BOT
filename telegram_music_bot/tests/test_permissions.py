from bot.utils.permissions import is_global_admin


def test_is_global_admin():
    assert is_global_admin(1, {1, 2})
    assert not is_global_admin(3, {1, 2})
