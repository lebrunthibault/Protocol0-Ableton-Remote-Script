from functools import partial

from typing import Optional

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import (
    TrackRecorderExternalSynthAudio,
)
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthClipSlot import \
    SourceClipSlot
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExport(TrackRecorderExternalSynthAudio):
    @property
    def recorded_cs(self):
        # type: () -> SourceClipSlot
        return SourceClipSlot(self.track.audio_track, self.recording_scene_index)

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export %s bars" % str(bar_length)

    def record(self, bar_length):
        # type: (float) -> Sequence
        return super(TrackRecorderExternalSynthAudioExport, self).record(bar_length * 2)

    def _focus_main_clip(self):
        # type: () -> Optional[Sequence]
        return None

    def post_record(self, bar_length):
        # type: (int) -> Optional[Sequence]
        seq = Sequence()
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).post_record, bar_length))

        seq.wait(11)

        seq.add(self.recorded_cs.post_record)
        seq.add(self._replace_clips)

        return seq.done()

    def _replace_clips(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self.recorded_cs.replace_clips)

        clips_replaced_count = len(self.recorded_cs.matching_clip_slots)
        seq.add(partial(Backend.client().show_success, "%s clips replaced" % clips_replaced_count))

        return seq.done()
