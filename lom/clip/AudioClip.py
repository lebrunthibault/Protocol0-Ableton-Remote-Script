from functools import partial

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
    def loop_end(self):
        # type: () -> float
        return super(AudioClip, self).loop_end

    # noinspection PyPropertyAccess
    @loop_end.setter
    def loop_end(self, loop_end):
        # type: (float) -> None
        # if self._clip and self.loop_start <= loop_end <= self.end_marker:
        self._clip.loop_end = loop_end

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

    @property
    def file_path(self):
        # type: () -> str
        return self._clip.file_path if self._clip else ""

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

    def play_and_mute(self):
        # type: () -> None
        self.muted = False
        seq = Sequence()
        seq.add(wait=1)  # wait for unmute
        seq.add(self.play)
        seq.add(wait_beats=2)  # 1 is not enough for session to arrangement
        seq.add(complete_on=self._playing_status_listener)  # clip has stopped
        seq.add(wait_beats=1)
        seq.add(partial(setattr, self, "muted", True))
        seq.done()
