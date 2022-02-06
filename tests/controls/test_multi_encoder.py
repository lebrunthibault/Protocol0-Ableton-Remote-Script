import pytest

from protocol0 import Protocol0
from protocol0.application.faderfox.EncoderAction import EncoderAction
from protocol0.application.faderfox.EncoderMoveEnum import EncoderMoveEnum
from protocol0.application.faderfox.MultiEncoder import MultiEncoder
from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.tests.fixtures import patch_song
from protocol0.tests.test_all import p0


class ActionGroupTest(ActionGroupMixin):
    CHANNEL = 1


def _press_encoder(encoder):
    # type: (MultiEncoder) -> None
    encoder._press_listener(1)
    encoder._press_listener(0)


def _scroll_encoder(encoder):
    # type: (MultiEncoder) -> None
    encoder._scroll_listener(1)


def _make_multi_encoder(identifier=1):
    # type: (int) -> MultiEncoder
    with p0.component_guard():
        patch_song()
        return ActionGroupTest(Protocol0.CONTAINER).add_encoder(identifier=identifier, name="pytest")


def test_multi_encoder_press():
    # type: () -> None
    res = {"pressed": False}

    def press():
        # type: () -> None
        res["pressed"] = True

    multi_encoder = _make_multi_encoder().add_action(EncoderAction(press, move_type=EncoderMoveEnum.PRESS, name="test"))

    with pytest.raises(Exception):
        multi_encoder.add_action(EncoderAction(func=lambda: None, move_type=EncoderMoveEnum.PRESS, name="test"))

    _press_encoder(multi_encoder)
    assert res["pressed"] is True


def test_multi_encoder_scroll():
    # type: () -> None
    res = {"scrolled": False}

    # noinspection PyUnusedLocal
    def scroll(go_next):
        # type: (bool) -> None
        res["scrolled"] = True

    multi_encoder = _make_multi_encoder().add_action(EncoderAction(scroll, move_type=EncoderMoveEnum.SCROLL, name="test"))
    _scroll_encoder(multi_encoder)
    assert res["scrolled"] is True


def test_multi_encoder_press_and_scroll():
    # type: () -> None
    res = {"pressed": False, "scrolled": False}

    # noinspection PyUnusedLocal
    def scroll(go_next):
        # type: (bool) -> None
        res["scrolled"] = True

    def press():
        # type: () -> None
        res["pressed"] = True

    multi_encoder = (
        _make_multi_encoder().add_action(EncoderAction(press, move_type=EncoderMoveEnum.PRESS, name="test")).add_action(
            EncoderAction(scroll, move_type=EncoderMoveEnum.SCROLL, name="test"))
    )
    _scroll_encoder(multi_encoder)
    assert res["scrolled"] is True
    assert res["pressed"] is False
    _press_encoder(multi_encoder)
    assert res["pressed"] is True
