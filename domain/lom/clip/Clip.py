from math import floor

from typing import TYPE_CHECKING, Optional, Any, List

import Live
from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.lom.clip.ClipActionMixin import ClipActionMixin
from protocol0.domain.lom.clip.ClipName import ClipName
from protocol0.domain.lom.device.DeviceParameter import DeviceParameter
from protocol0.domain.shared.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class Clip(ClipActionMixin, AbstractObject):
    __subject_events__ = ("notes", "length")

    def __init__(self, clip_slot, *a, **k):
        # type: (ClipSlot, Any, Any) -> None
        super(Clip, self).__init__(*a, **k)
        self.clip_slot = clip_slot
        self._clip_slot = clip_slot._clip_slot
        self._clip = self._clip_slot.clip  # type: Live.Clip.Clip
        self.view = self._clip.view  # type: Live.Clip.Clip.View
        self.track = clip_slot.track  # type: SimpleTrack

        # listeners
        self._playing_status_listener.subject = self._clip
        self._loop_start_listener.subject = self._clip
        self._loop_end_listener.subject = self._clip

        self.clip_name = ClipName(self)
        self.displayed_automated_parameter = None  # type: Optional[DeviceParameter]

    def __eq__(self, clip):
        # type: (object) -> bool
        return isinstance(clip, Clip) and self._clip == clip._clip

    def _on_selected(self):
        # type: () -> None
        self.show_loop()

    @property
    def index(self):
        # type: () -> int
        return self.clip_slot.index

    @p0_subject_slot("playing_status")
    def _playing_status_listener(self):
        # type: () -> None
        pass

    @p0_subject_slot("loop_start")
    def _loop_start_listener(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        self.notify_length()

    @p0_subject_slot("loop_end")
    def _loop_end_listener(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        self.notify_length()

    @staticmethod
    def make(clip_slot, is_new=False):
        # type: (ClipSlot, bool) -> Clip
        clip = clip_slot.CLIP_CLASS(clip_slot=clip_slot)

        if is_new:
            clip.configure_new_clip()

        return clip

    @property
    def name(self):
        # type: () -> str
        return self._clip.name if getattr(self, "_clip", None) else None

    # noinspection PyPropertyAccess
    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._clip and name:
            self._clip.name = str(name).strip()

    @property
    def length(self):
        # type: () -> int
        """
        For looped clips: loop length in beats.
        Casting to int to have whole beats.
        not using unwarped audio clips
        """
        length = int(floor(self._clip.length)) if self._clip and getattr(self, "warping", True) else 0
        return length

    @length.setter
    def length(self, length):
        # type: (int) -> None
        self.loop_end = self.loop_start + length
        self.end_marker = self.loop_end

    @property
    def bar_length(self):
        # type: () -> int
        return int(self.length / self.song.signature_numerator)

    @bar_length.setter
    def bar_length(self, bar_length):
        # type: (int) -> None
        self.length = bar_length * self.song.signature_numerator

    @property
    def looping(self):
        # type: () -> bool
        return self._clip.looping if self._clip else False

    # noinspection PyPropertyAccess
    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        if self._clip:
            self._clip.looping = looping

    @property
    def loop_start(self):
        # type: () -> float
        return self._clip.loop_start if self._clip else 0

    # noinspection PyPropertyAccess
    @loop_start.setter
    def loop_start(self, loop_start):
        # type: (float) -> None
        if self._clip and loop_start < self.loop_end:
            self._clip.loop_start = loop_start

    @property
    def loop_end(self):
        # type: () -> float
        return self._clip.loop_end if self._clip else 0

    # noinspection PyPropertyAccess
    @loop_end.setter
    def loop_end(self, loop_end):
        # type: (float) -> None
        if self._clip and loop_end > self.loop_start:
            self._clip.loop_end = loop_end

    @property
    def start_marker(self):
        # type: () -> float
        return self._clip.start_marker if self._clip else 0

    # noinspection PyPropertyAccess
    @start_marker.setter
    def start_marker(self, start_marker):
        # type: (float) -> None
        if self._clip and start_marker < self.end_marker:
            self._clip.start_marker = start_marker

    @property
    def end_marker(self):
        # type: () -> float
        return self._clip.end_marker if self._clip else 0

    # noinspection PyPropertyAccess
    @end_marker.setter
    def end_marker(self, end_marker):
        # type: (float) -> None
        if self._clip and end_marker > self.start_marker:
            self._clip.end_marker = end_marker

    @property
    def color(self):
        # type: () -> int
        return self._clip.color_index if self._clip else 0

    # noinspection PyPropertyAccess
    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        if self._clip:
            self._clip.color_index = color_index

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

    # @property
    # def mute(self):
    #     # type: () -> bool
    #     raise Protocol0Error("Use clip.muted, not clip.mute")

    @property
    def muted(self):
        # type: () -> bool
        return self._clip and self._clip.muted

    # noinspection PyPropertyAccess
    @muted.setter
    def muted(self, muted):
        # type: (bool) -> None
        if self._clip:
            self._clip.muted = muted

    @property
    def automated_parameters(self):
        # type: () -> List[DeviceParameter]
        return [parameter for parameter in self.track.device_parameters if self.automation_envelope(parameter)]

    def disconnect(self):
        # type: () -> None
        super(Clip, self).disconnect()
        if self.clip_name:
            self.clip_name.disconnect()