"""Tests for delivery module."""

from nightshift.delivery import TelegramDelivery


def test_split_message_short():
    chunks = TelegramDelivery._split_message("short message", max_len=100)
    assert chunks == ["short message"]


def test_split_message_long():
    text = "line one\nline two\nline three\nline four"
    chunks = TelegramDelivery._split_message(text, max_len=20)
    assert len(chunks) > 1
    # All content preserved
    assert "line one" in "".join(chunks)
    assert "line four" in "".join(chunks)
