import pytest

from bot.utils.callback_data import CallbackDataCodec


def test_codec_roundtrip():
    c = CallbackDataCodec('secret')
    data = c.encode('x', 1, 2, 'p')
    decoded = c.decode(data)
    assert decoded['action'] == 'x'


def test_codec_reject_bad_sig():
    c = CallbackDataCodec('secret')
    data = c.encode('x', 1, 2, 'p') + 'a'
    with pytest.raises(ValueError):
        c.decode(data)
