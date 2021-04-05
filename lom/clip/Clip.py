from functools import partial

from typing import TYPE_CHECKING, Optional

import Live

from a_protocol_0.enums.ClipTypeEnum import ClipTypeEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.ClipActionMixin import ClipActionMixin
from a_protocol_0.lom.clip.ClipName import ClipName
from a_protocol_0.utils.decorators import p0_subject_slot, is_change_deferrable

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class Clip(ClipActionMixin, AbstractObject):
    __subject_events__ = ('notes', 'linked')

    def __init__(self, clip_slot, set_clip_name=True, is_new=False, *a, **k):
        # type: (ClipSlot) -> None
        super(Clip, self).__init__(*a, **k)
        self.clip_slot = clip_slot
        self._clip_slot = clip_slot._clip_slot
        self._clip = self._clip_slot.clip  # type: Live.Clip.Clip
        self.linked_clip = None  # type: Optional[Clip]
        self.view = self._clip.view  # type: Live.Clip.Clip.View
        self.index = clip_slot.index
        self.track = clip_slot.track  # type: SimpleTrack
        self.is_selected = False
        self._previous_name = self._clip.name
        self._notes_listener.subject = self._clip
        self._color_listener.subject = self._clip
        self._is_recording_listener.subject = self._clip
        self.color = self.track.base_color
        self.clip_name = ClipName(self) if set_clip_name else None
        # handles duplicate clips
        if self.clip_name and is_new:
            self.clip_name.set_clip_name(is_playable=False)

    def _on_selected(self):
        pass

    @p0_subject_slot("notes")
    def _notes_listener(self):
        pass

    @p0_subject_slot("is_recording")
    def _is_recording_listener(self):
        pass

    @staticmethod
    def make(clip_slot, is_new=False):
        # type: (ClipSlot) -> Clip
        from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
        from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
        from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
        from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip
        from a_protocol_0.lom.clip.AudioClip import AudioClip
        from a_protocol_0.lom.clip.MidiClip import MidiClip

        class_ = None
        if isinstance(clip_slot, AutomationMidiClipSlot):
            class_ = AutomationMidiClip
        elif isinstance(clip_slot.track, AutomationAudioTrack):
            class_ = AutomationAudioClip
        elif clip_slot.track.is_audio:
            class_ = AudioClip
        elif clip_slot.track.is_midi:
            class_ = MidiClip
        else:
            raise Protocol0Error("Couldn't generate clip for track %s" % clip_slot.track)

        clip = class_(clip_slot=clip_slot, is_new=is_new)

        if is_new:
            clip.configure_new_clip()

        return clip

    @property
    def type(self):
        # type: () -> ClipTypeEnum
        return ClipTypeEnum.get_from_value(self.clip_name.base_name.split(" ")[0])

    @property
    def name(self):
        # type: () -> str
        return self._clip.name if getattr(self, "_clip", None) else None

    @name.setter
    @is_change_deferrable
    def name(self, name):
        # type: (str) -> None
        if self._clip and str(name) != self._clip.name:
            self._clip.name = str(name)

    @property
    def length(self):
        # type: () -> float
        """ For looped clips: loop length in beats """
        return self._clip.length if self._clip else 0

    @property
    def looping(self):
        # type: () -> float
        return self._clip.looping if self._clip else 0

    @looping.setter
    @is_change_deferrable
    def looping(self, looping):
        # type: (float) -> None
        # enforce looping
        if self._clip and looping:
            self._clip.looping = looping

    @property
    def loop_start(self):
        # type: () -> float
        return self._clip.loop_start if self._clip else 0

    @loop_start.setter
    @is_change_deferrable
    def loop_start(self, loop_start):
        # type: (float) -> None
        if self._clip:
            self._clip.loop_start = loop_start

    @property
    def loop_end(self):
        # type: () -> float
        return self._clip.loop_end if self._clip else 0

    @loop_end.setter
    @is_change_deferrable
    def loop_end(self, loop_end):
        # type: (float) -> None
        if self._clip:
            self._clip.loop_end = loop_end

    @property
    def start_marker(self):
        # type: () -> float
        return self._clip.start_marker if self._clip else 0

    @start_marker.setter
    @is_change_deferrable
    def start_marker(self, start_marker):
        # type: (float) -> None
        if self._clip:
            self._clip.start_marker = start_marker

    @property
    def end_marker(self):
        # type: () -> float
        return self._clip.end_marker if self._clip else 0

    @end_marker.setter
    @is_change_deferrable
    def end_marker(self, end_marker):
        # type: (float) -> None
        if self._clip:
            self._clip.end_marker = end_marker

    @p0_subject_slot("color")
    def _color_listener(self):
        self.parent.defer(partial(setattr, self, "color", int(self.track.base_color)))

    @property
    def color(self):
        # type: () -> int
        return self._clip.color_index if self._clip else 0

    @color.setter
    @is_change_deferrable
    def color(self, color_index):
        # type: (int) -> None
        if self._clip and self._clip.color_index != self.track.base_color:
            self._clip.color_index = int(self.track.base_color)

    @property
    def is_playing(self):
        # type: () -> bool
        return self._clip and self._clip.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        if self._clip and is_playing != self.is_playing:
            self._clip.is_playing = is_playing

    @property
    def is_triggered(self):
        # type: () -> bool
        return self._clip and self._clip.is_triggered

    @property
    def playing_position(self):
        # type: () -> float
        """ For MIDI and warped audio clips the value is given in beats of absolute clip time """
        return self._clip.playing_position if self._clip else 0

    @property
    def is_recording(self):
        # type: () -> bool
        return self._clip and self._clip.is_recording

    def disconnect(self):
        super(Clip, self).disconnect()
        if self.clip_name:
            self.clip_name.disconnect()
