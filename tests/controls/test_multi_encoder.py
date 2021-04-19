import pytest
from typing import Any

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.controls.EncoderAction import EncoderAction
from a_protocol_0.controls.EncoderModifierEnum import EncoderModifierEnum
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.tests.test_all import p0


class ActionGroupTest(AbstractActionGroup):
    def __init__(self, channel=0, *a, **k):
        # type: (int, Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=channel, record_actions_as_global=False, *a, **k)


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
        return ActionGroupTest().add_encoder(id=identifier, name="pytest")


def test_multi_encoder_press():
    # type: () -> None
    res = {"pressed": False}

    def press():
        # type: () -> None
        res["pressed"] = True

    with p0.component_guard():
        action_group = ActionGroupTest()
        multi_encoder = action_group.add_encoder(id=2, name="pytest", on_press=press)

    with pytest.raises(Exception):
        multi_encoder.add_action(EncoderAction(func=lambda: None))

    press_encoder(multi_encoder)
    assert res["pressed"] is True


def test_multi_encoder_scroll():
    # type: () -> None
    res = {"scrolled": False}

    def scroll(go_next):
        # type: (bool) -> None
        res["scrolled"] = True

    with p0.component_guard():
        action_group = ActionGroupTest()
        multi_encoder = action_group.add_encoder(id=2, name="pytest", on_scroll=scroll)

    scroll_encoder(multi_encoder)
    assert res["scrolled"] is True


def test_multi_encoder_press_and_scroll():
    # type: () -> None
    res = {"pressed": False, "scrolled": False}

    def scroll(go_next):
        # type: (bool) -> None
        res["scrolled"] = True

    def press():
        # type: () -> None
        res["pressed"] = True

    with p0.component_guard():
        action_group = ActionGroupTest()
        multi_encoder = action_group.add_encoder(id=2, name="pytest", on_press=press, on_scroll=scroll)

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
        action_group = ActionGroupTest()
        action_group.add_modifier(id=1, modifier_type=EncoderModifierEnum.SHIFT)
        multi_encoder = action_group.add_encoder(id=2, name="pytest", on_shift_press=shift_press)

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
    multi_encoder.add_action(EncoderAction(func=dup_press, modifier_type=EncoderModifierEnum.DUPX))

    press_encoder(multi_encoder)
    assert res["dup_pressed"] is False

    multi_encoder.get_modifier_from_enum(EncoderModifierEnum.DUPX).pressed = True
    press_encoder(multi_encoder)
    assert res["dup_pressed"] is True
