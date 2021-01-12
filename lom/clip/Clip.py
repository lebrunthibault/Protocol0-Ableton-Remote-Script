from typing import TYPE_CHECKING, List
import Live

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.ClipActionMixin import ClipActionMixin
from a_protocol_0.lom.Note import Note
from a_protocol_0.utils.decorators import defer

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot


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
        # memorizing notes for note change comparison
        self._prev_notes = []  # type: List[Note]
        self._prev_notes = self.get_notes() if self._clip.is_midi_clip else []  # type: List[Note]
        self._added_note = None  # type: Note
        self._is_updating_notes = False
        self.color = self.track.base_color

    def __repr__(self):
        repr = super(Clip, self).__repr__()
        return "%s (%s)" % (repr, self.track)

    @staticmethod
    def make_clip(clip_slot):
        # type: (ClipSlot) -> Clip
        from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
        if isinstance(clip_slot.track, AutomationMidiTrack):
            from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
            return AutomationMidiClip(clip_slot=clip_slot)
        else:
            return Clip(clip_slot=clip_slot)

    @property
    def name(self):
        # type: () -> str
        return self._clip.name if self._clip else None

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._clip and name != self._clip.name:
            self._clip.name = name

    @property
    def length(self):
        # type: () -> float
        """ For looped clips: loop length in beats """
        return self._clip.length if self._clip else 0

    @property
    def loop_start(self):
        # type: () -> float
        """ For looped clips: loop length in beats """
        return self._clip.loop_start if self._clip else 0

    @property
    def color(self):
        # type: () -> int
        return self._clip.color_index if self._clip else 0

    @color.setter
    @defer
    def color(self, color_index):
        # type: (int) -> None
        if self._clip and color_index != self._clip.color_index:
            self._clip.color_index = int(color_index)

    @property
    def is_playing(self):
        # type: () -> bool
        return self._clip and self._clip.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        if self._clip:
            self._clip.is_playing = is_playing

    @property
    def playing_position(self):
        # type: () -> float
        """ For MIDI and warped audio clips the value is given in beats of absolute clip time """
        return self._clip.playing_position if self._clip else 0

    @playing_position.setter
    def playing_position(self, playing_position):
        # type: (float) -> None
        if self._clip:
            self._clip.playing_position = playing_position

    @property
    def is_recording(self):
        # type: () -> bool
        return self._clip and self._clip.is_recording

    def disconnect(self):
        super(Clip, self).disconnect()