from typing import TYPE_CHECKING, List
import Live

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.ClipActionMixin import ClipActionMixin
from a_protocol_0.lom.Note import Note
from a_protocol_0.utils.decorators import defer, subject_slot
from a_protocol_0.utils.log import log_ableton

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot


class Clip(ClipActionMixin, AbstractObject):
    __subject_events__ = ('notes', 'name')

    def __init__(self, clip_slot, *a, **k):
        # type: (ClipSlot) -> None
        super(Clip, self).__init__(*a, **k)
        self.clip_slot = clip_slot
        self._clip_slot = clip_slot._clip_slot
        self._clip = self._clip_slot.clip  # type: Live.Clip.Clip
        self.index = clip_slot.index
        self.track = clip_slot.track
        self.is_selected = False
        self._notes_listener.subject = self._clip
        self._name_listener.subject = self._clip
        # memorizing notes for note change comparison
        self._prev_notes = []  # type: List[Note]  # here: trying to use get_notes results in a bug caused by the debounce set on notes_listener
        self._added_note = None  # type: Note
        self._is_updating_notes = False
        self.color = self.track.base_color

    def __repr__(self):
        repr = super(Clip, self).__repr__()
        return "%s (%s)" % (repr, self.track)

    @subject_slot("notes")
    def _notes_listener(self):
        pass

    @subject_slot("name")
    def _name_listener(self):
        # noinspection PyUnresolvedReferences
        self.parent.defer(self.notify_name)

    @staticmethod
    def make(clip_slot):
        # type: (ClipSlot) -> Clip
        from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
        from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
        from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot
        from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip
        if isinstance(clip_slot, AutomationMidiClipSlot):
            return AutomationMidiClip(clip_slot=clip_slot)
        elif isinstance(clip_slot, AutomationAudioClipSlot):
            return AutomationAudioClip(clip_slot=clip_slot)
        else:
            return Clip(clip_slot=clip_slot)

    @property
    def name(self):
        # type: () -> str
        return self._clip.name if getattr(self, "_clip", None) else None

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if getattr(self, "_clip", None) and name != self._clip.name:
            self._clip.name = name

    @property
    def length(self):
        # type: () -> float
        """ For looped clips: loop length in beats """
        return self._clip.length if self._clip else 0

    @property
    def warping(self):
        # type: () -> float
        return self._clip.warping if self._clip else 0

    @warping.setter
    def warping(self, warping):
        # type: (float) -> None
        self._clip.warping = warping

    @property
    def looping(self):
        # type: () -> float
        return self._clip.looping if self._clip else 0

    @looping.setter
    def looping(self, looping):
        # type: (float) -> None
        self._clip.looping = looping

    @property
    def loop_start(self):
        # type: () -> float
        return self._clip.loop_start if self._clip else 0

    @loop_start.setter
    def loop_start(self, loop_start):
        # type: (float) -> None
        self._clip.loop_start = loop_start

    @property
    def loop_end(self):
        # type: () -> float
        return self._clip.loop_end if self._clip else 0

    @loop_end.setter
    def loop_end(self, loop_end):
        # type: (float) -> None
        self._clip.loop_end = loop_end

    @property
    def start_marker(self):
        # type: () -> float
        return self._clip.start_marker if self._clip else 0

    @start_marker.setter
    def start_marker(self, start_marker):
        # type: (float) -> None
        self._clip.start_marker = start_marker

    @property
    def end_marker(self):
        # type: () -> float
        return self._clip.end_marker if self._clip else 0

    @end_marker.setter
    def end_marker(self, end_marker):
        # type: (float) -> None
        self._clip.end_marker = end_marker

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
