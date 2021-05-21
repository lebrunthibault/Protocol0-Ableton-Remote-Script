from typing import Tuple

from a_protocol_0.enums.AbstractEnum import AbstractEnum


class ColorEnum(AbstractEnum):
    SIMPLER = 2
    DRUM_RACK = 3
    DEFAULT = 10
    DISABLED = 13
    SERUM = 18
    PROPHET = 23
    ADDICTIVE_KEYS = 26
    MINITAUR = 69


class InterfaceColorEnum(AbstractEnum):
    @classmethod
    def get_tuple_from_string(cls, color):
        # type: (str) -> Tuple[int, int, int]
        return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))

    @classmethod
    def get_string_from_tuple(cls, color):
        # type: (Tuple[int, int, int]) -> str
        return "".join(str(hex(code).replace("0x", "")) for code in color)

    def get_tuple(self):
        # type: () -> Tuple[int, int, int]
        return InterfaceColorEnum.get_tuple_from_string(self.value)

    ACTIVATED = "FFA608"
    DEACTIVATED = "2D2D2D"
    SEPARATOR = "5F5F5F"
