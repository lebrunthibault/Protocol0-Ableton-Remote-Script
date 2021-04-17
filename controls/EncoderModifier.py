from a_protocol_0.enums.AbstractEnum import AbstractEnum
from a_protocol_0.lom.AbstractObject import AbstractObject


class EncoderModifierEnum(AbstractEnum):
    SHIFT = "SHIFT"
    PLAY_STOP = "PLAY_STOP"
    SOLO = "SOLO"
    FOLD = "FOLD"
    DUPX = "DUPLICATE"


class EncoderModifier(AbstractObject):
    def __init__(self, modifier_type, *a, **k):
        # type: (EncoderModifierEnum) -> None
        super(EncoderModifier, self).__init__(*a, **k)
        self.type = modifier_type
        self.pressed = False

    def __repr__(self):
        return "%s(%s)" % (super(EncoderModifier, self).__repr__(), self.type.value)
