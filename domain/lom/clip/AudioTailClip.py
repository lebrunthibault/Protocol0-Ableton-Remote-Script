from functools import partial

from typing import TYPE_CHECKING

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
    from protocol0.domain.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot


class AudioTailClip(AudioClip):
    def __init__(self, clip_slot):
        # type: (AudioTailClipSlot) -> None
        super(AudioTailClip, self).__init__(clip_slot)
        self.track = self.track  # type: SimpleAudioTailTrack
        self.clip_slot = self.clip_slot  # type: AudioTailClipSlot

    @property
    def loop_end(self):
        # type: () -> float
        return super(AudioTailClip, self).loop_end

    # noinspection PyPropertyAccess
    @loop_end.setter
    def loop_end(self, loop_end):
        # type: (float) -> None
        """ make clip synchronizer work with the clip tail """
        self.loop_start = loop_end

    def post_record(self, bar_length):
        # type: (int) -> None
        Logger.log_dev("bar_length: %s" % bar_length)
        super(AudioTailClip, self).post_record(bar_length)
        if bar_length == 0:
            return None
        self.clip_name.update(base_name="")
        clip_end = bar_length * SongFacade.signature_numerator()
        Logger.log_dev("clip_end: %s" % clip_end)
        Logger.log_dev("self.loop_start: %s" % self.loop_start)
        Logger.log_dev("self.loop_end: %s" % self.loop_end)
        Logger.log_dev("self.length: %s" % self.length)

        self.looping = False
        self.loop_start = clip_end
        self.muted = True

    def play_and_mute(self):
        # type: () -> Sequence
        self.muted = False
        seq = Sequence()
        seq.add(wait=1)  # wait for unmute
        seq.add(self.fire)
        seq.add(wait_beats=1)
        seq.add(complete_on=self._playing_status_listener)
        seq.add(wait=10)
        seq.add(partial(setattr, self, "muted", True))
        return seq.done()
