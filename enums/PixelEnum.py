from typing import Tuple

from protocol0.enums.AbstractEnum import AbstractEnum


class PixelEnum(AbstractEnum):
    FOLD_CLIP_NOTES = (418, 686)
    SHOW_CLIP_ENVELOPE = (86, 1014)

    @property
    def coordinates(self):
        # type: () -> Tuple[int, int]
        return self.value
