from typing import Tuple

from protocol0.shared.AbstractEnum import AbstractEnum


class PixelEnum(AbstractEnum):
    SAVE_SAMPLE = (534, 1316)

    @property
    def coordinates(self):
        # type: () -> Tuple[int, int]
        return self.value
