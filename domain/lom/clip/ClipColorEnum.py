from protocol0.domain.shared.ColorEnumInterface import ColorEnumInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class ClipColorEnum(ColorEnumInterface, AbstractEnum):
    AUDIO_UN_QUANTIZED = 13

    @property
    def color_int_value(self):
        # type: () -> int
        return self.value
