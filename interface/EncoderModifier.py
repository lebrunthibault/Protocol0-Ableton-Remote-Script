from typing import Any

from a_protocol_0.interface.EncoderModifierEnum import EncoderModifierEnum
from a_protocol_0.lom.AbstractObject import AbstractObject


class EncoderModifier(AbstractObject):
    def __init__(self, modifier_type, *a, **k):
        # type: (EncoderModifierEnum, Any, Any) -> None
        super(EncoderModifier, self).__init__(*a, **k)
        self.type = modifier_type
        self.pressed = False

    def __repr__(self):
        # type: () -> str
        return "%s(%s)" % (super(EncoderModifier, self).__repr__(), self.type.value)
