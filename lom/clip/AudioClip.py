from functools import partial
from math import floor

from typing import TYPE_CHECKING, Any

import Live
from protocol0.enums.PixelEnum import PixelEnum
from protocol0.lom.clip.Clip import Clip
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
    from protocol0.lom.clip_slot.AudioClipSlot import AudioClipSlot


# noinspection PyPropertyAccess
class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleAudioTrack
        self.clip_slot = self.clip_slot  # type: AudioClipSlot
        self._warping_listener.subject = self._clip

    @p0_subject_slot("warping")
    def _warping_listener(self):
        # type: () -> None
        if self.warping:
            self.parent.defer(partial(setattr, self, "looping", True))
        # noinspection PyUnresolvedReferences
        self.notify_length()

    @property
    def warping(self):
        # type: () -> float
        return self._clip.warping if self._clip else 0

    @warping.setter
    def warping(self, warping):
        # type: (float) -> None
        if self._clip:
            self._clip.warping = warping

    @property
    def warp_mode(self):
        # type: () -> Live.Clip.WarpMode
        return self._clip.warp_mode if self._clip else Live.Clip.WarpMode.beats

    @warp_mode.setter
    def warp_mode(self, warp_mode):
        # type: (Live.Clip.WarpMode) -> None
        if self._clip:
            self._clip.warp_mode = warp_mode

    @p0_subject_slot("looping")
    def _looping_listener(self):
        # type: () -> None
        if self.warping:
            # enforce looping
            self.parent.defer(partial(setattr, self._clip, "looping", True))

    @property
    def file_path(self):
        # type: () -> str
        return self._clip.file_path if self._clip else ""

    @property
    def has_tail(self):
        # type: () -> bool
        total_length = floor(self.end_marker - self.start_marker)
        return total_length > self.length

    def post_record(self):
        # type: () -> None
        super(AudioClip, self).post_record()
        self.warp_mode = Live.Clip.WarpMode.complex

    def crop(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(partial(self.system.right_click, 1202, 809))
        seq.add(partial(self.system.click, 1262, 413))
        seq.add(wait=2)
        return seq.done()

    def save_sample(self):
        # type: () -> None
        self.system.click_vertical_zone(*PixelEnum.SAVE_SAMPLE.coordinates)

    def post_record_clip_tail(self):
        # type: (AudioClip) -> None
        self.loop_start = self.song.signature_numerator  # offset one bar
        self.move_playing_pos(self.song.signature_numerator)  # keep it sync with scene
        self.clip_name.update()
