from functools import partial

from typing import Any, Optional

from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
# noinspection PyPropertyAccess
from protocol0.sequence.Sequence import Sequence


class AudioClipSlot(ClipSlot):
    CLIP_CLASS = AudioClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioClip]
        self.previous_audio_file_path = None  # type: Optional[str]
        if self.clip:
            self.previous_audio_file_path

    def record(self, bar_length, record_tail=False):
        # type: (int, bool) -> Optional[Sequence]
        record_tail = self.track.abstract_track.record_clip_tails
        seq = Sequence()
        seq.add(partial(super(AudioClipSlot, self).record, bar_length=bar_length, record_tail=record_tail))
        if record_tail:
            seq.add(wait=1)
            seq.add(self.post_record_clip_tail)

        return seq.done()

    def post_record_clip_tail(self):
        # type: () -> None
        clip_end = self.clip.end_marker - self.song.signature_numerator  # one bar tail

        from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
        if isinstance(self.track, SimpleAudioTailTrack):
            self.clip.start_marker = self.clip.loop_start = clip_end
            self.clip.looping = False
            self.clip.muted = True
        else:
            self.clip.loop_end = clip_end
            self.clip.end_marker = clip_end

        self.clip.clip_name.update()
