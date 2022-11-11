from typing import List

from protocol0.domain.lom.clip.ClipNameEnum import ClipNameEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioExport import \
    TrackRecorderExternalSynthAudioExport
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExportOnce(TrackRecorderExternalSynthAudioExport):
    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export once %s bars" % str(bar_length)

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return [self.track.audio_track]

    def record(self, bar_length):
        # type: (float) -> Sequence
        # bypass recording on the tail track
        if self.track.audio_tail_track is not None:
            self.track.audio_tail_track.arm_state.unarm()

        return super(TrackRecorderExternalSynthAudioExportOnce, self).record(bar_length)

    def _configure_clips(self, bar_length):
        # type: (int) -> None
        self.atk_cs.clip.name = ClipNameEnum.ONCE.value

        length = bar_length * SongFacade.signature_numerator()
        self.atk_cs.clip.loop._clip.loop_end = length
