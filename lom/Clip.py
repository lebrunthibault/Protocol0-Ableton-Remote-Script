from typing import TYPE_CHECKING
import Live

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.ClipActionMixin import ClipActionMixin

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.ClipSlot import ClipSlot


class Clip(ClipActionMixin, AbstractObject):
    def __init__(self, clip_slot, *a, **k):
        # type: (ClipSlot) -> None
        super(Clip, self).__init__(*a, **k)
        self.clip_slot = clip_slot
        self._clip_slot = clip_slot._clip_slot
        self._clip = self._clip_slot.clip  # type: Live.Clip.Clip
        self.index = clip_slot.index
        self.track = clip_slot.track
        self.is_selected = False

    @property
    def name(self):
        # type: () -> str
        return self._clip.name

    @property
    def length(self):
        # type: () -> float
        """ For looped clips: loop length in beats """
        return self._clip.length

    @property
    def color(self):
        # type: () -> int
        return self._clip.color_index

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self._clip.color_index = color_index

    @property
    def is_playing(self):
        # type: () -> bool
        return self._clip.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        self._clip.is_playing = is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self._clip.is_recording
