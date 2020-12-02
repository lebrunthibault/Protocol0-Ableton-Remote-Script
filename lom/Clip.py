from typing import Any, Optional, TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.ClipActionMixin import ClipActionMixin

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class Clip(ClipActionMixin, AbstractObject):
    def __init__(self, clip, index, track, *a, **k):
        # type: (Any, int, Optional[SimpleTrack], Any, Any) -> None
        super(Clip, self).__init__(*a, **k)
        self._clip = clip
        self.index = index
        self.track = track

    def __nonzero__(self):
        return self._clip is not None

    def __eq__(self, other):
        if isinstance(other, Clip):
            return self._clip == other._clip
        return False

    @classmethod
    def empty_clip(cls):
        # type: () -> Clip
        return Clip(clip=None, index=-1, track=None)

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
        return self.index >= 0 and self._clip.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        if self.index >= 0:
            self._clip.is_playing = is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self._clip and self._clip.is_recording
