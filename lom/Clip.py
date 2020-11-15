from typing import Any, Optional, TYPE_CHECKING

from a_protocol_0.actions.mixins.ClipActionMixin import ClipActionMixin

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class Clip(ClipActionMixin):
    def __init__(self, clip_slot, index, track):
        # type: (Optional[Any], int, Optional["SimpleTrack"]) -> None
        self.clip_slot = clip_slot
        self.clip = clip_slot.clip if clip_slot else None
        self.index = index
        self.track = track

    def __nonzero__(self):
        return self.clip is not None

    def __eq__(self, other):
        if isinstance(other, Clip):
            return self.clip == other.clip
        return False

    @classmethod
    def empty_clip(cls):
        # type: () -> Clip
        return Clip(None, -1, None)

    @property
    def length(self):
        # type: () -> float
        """ For looped clips: loop length in beats """
        return self.clip.length

    @property
    def name(self):
        # type: () -> str
        return self.clip.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self.clip:
            self.clip.name = name

    @property
    def color(self):
        # type: () -> int
        return self.clip.color_index

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.clip.color_index = color_index

    @property
    def is_playing(self):
        # type: () -> bool
        return self.index >= 0 and self.clip.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        if self.index >= 0:
            self.clip.is_playing = is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.clip and self.clip.is_recording

    @property
    def playing_position(self):
        # type: () -> float
        """
        For MIDI and warped audio clips the value is given in beats of absolute clip time. Zero beat time of the clip is where 1 is shown in the bar/beat/16th time scale at the top of the clip view.
        """
        return self.clip.playing_position
