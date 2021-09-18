import pytest
from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.interface.EncoderAction import EncoderAction
from protocol0.interface.EncoderModifierEnum import EncoderModifierEnum
from protocol0.interface.EncoderMoveEnum import EncoderMoveEnum
from protocol0.interface.MultiEncoder import MultiEncoder
from protocol0.tests.fixtures import make_song
from protocol0.tests.test_all import p0


class ActionGroupTest(AbstractActionGroup):
    def __init__(self, channel=0, *a, **k):
        # type: (int, Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=channel, *a, **k)


def press_encoder(encoder):
    # type: (MultiEncoder) -> None
    encoder._press_listener(1)
    encoder._press_listener(0)


def scroll_encoder(encoder):
    # type: (MultiEncoder) -> None
    encoder._scroll_listener(1)


def make_multi_encoder(identifier=1):
    # type: (int) -> MultiEncoder
    with p0.component_guard():
        p0.protocol0_song = make_song(count_simple_tracks=1)
        return ActionGroupTest().add_encoder(identifier=identifier, name="pytest")


def test_multi_encoder_press():
    # type: () -> None
    res = {"pressed": False}

    def press():
        # type: () -> None
        res["pressed"] = True

    multi_encoder = make_multi_encoder().add_action(EncoderAction(press))

    with pytest.raises(Exception):
        multi_encoder.add_action(EncoderAction(func=lambda: None))

    press_encoder(multi_encoder)
    assert res["pressed"] is True


def test_multi_encoder_scroll():
    # type: () -> None
    res = {"scrolled": False}

    # noinspection PyUnusedLocal
    def scroll(go_next):
        # type: (bool) -> None
        res["scrolled"] = True

    multi_encoder = make_multi_encoder().add_action(EncoderAction(scroll, move_type=EncoderMoveEnum.SCROLL))
    scroll_encoder(multi_encoder)
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
        make_multi_encoder()
        .add_action(EncoderAction(press))
        .add_action(EncoderAction(scroll, move_type=EncoderMoveEnum.SCROLL))
    )
    scroll_encoder(multi_encoder)
    assert res["scrolled"] is True
    assert res["pressed"] is False
    press_encoder(multi_encoder)
    assert res["pressed"] is True


def test_multi_encoder_shift_press():
    # type: () -> None
    res = {"shift_pressed": False}

    def shift_press():
        # type: () -> None
        res["shift_pressed"] = True

    with p0.component_guard():
        multi_encoder = make_multi_encoder()
        multi_encoder.add_action(EncoderAction(func=shift_press, modifier_type=EncoderModifierEnum.SHIFT))
        multi_encoder._group.add_modifier(identifier=2, modifier_type=EncoderModifierEnum.SHIFT)

    press_encoder(multi_encoder)
    assert res["shift_pressed"] is False

    multi_encoder.get_modifier_from_enum(EncoderModifierEnum.SHIFT).pressed = True
    press_encoder(multi_encoder)
    assert res["shift_pressed"] is True


def test_multi_encoder_dup_press():
    # type: () -> None
    res = {"dup_pressed": False}

    def dup_press():
        # type: () -> None
        res["dup_pressed"] = True

    multi_encoder = make_multi_encoder()
    multi_encoder.add_action(EncoderAction(func=dup_press, modifier_type=EncoderModifierEnum.DUP))

    press_encoder(multi_encoder)
    assert res["dup_pressed"] is False

    multi_encoder.get_modifier_from_enum(EncoderModifierEnum.DUP).pressed = True
    press_encoder(multi_encoder)
    assert res["dup_pressed"] is True
