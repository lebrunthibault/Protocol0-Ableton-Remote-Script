from typing import Tuple

from protocol0.shared.AbstractEnum import AbstractEnum


class PixelEnum(AbstractEnum):
    SHOW_CLIP_ENVELOPE = (86, 1014)
    SAVE_SAMPLE = (267, 658)

    @property
    def coordinates(self):
        # type: () -> Tuple[int, int]
        return self.value
