import pytest

from bot.utils.callback_data import CallbackSigner


def test_callback_sign_verify():
    signer = CallbackSigner("secret")
    token = signer.sign("pick:1:2:3:url")
    assert signer.verify(token) == "pick:1:2:3:url"


def test_callback_rejects_tamper():
    signer = CallbackSigner("secret")
    token = signer.sign("abc") + "x"
    with pytest.raises(Exception):
        signer.verify(token)
