from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipSelectedEvent(object):
    def __init__(self, clip):
        # type: (Clip) -> None
        self.clip = clip
