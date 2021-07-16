from typing import Any

from protocol0.interface.EncoderModifierEnum import EncoderModifierEnum
from protocol0.interface.MultiEncoder import MultiEncoder
from protocol0.utils.decorators import p0_subject_slot


class MultiEncoderModifier(MultiEncoder):
    """
    This represent an encoder button. Pressing it will activate the configured modifier for the active group.
    Only one modifier can be pressed at a time.
    """

    def __init__(self, modifier_type, *a, **k):
        # type: (EncoderModifierEnum, Any, Any) -> None
        super(MultiEncoderModifier, self).__init__(name=modifier_type.name, *a, **k)
        self.modifier_type = modifier_type

    @p0_subject_slot("value")
    def _press_listener(self, value):
        # type: (int) -> None
        self.get_modifier_from_enum(self.modifier_type).pressed = bool(value)
