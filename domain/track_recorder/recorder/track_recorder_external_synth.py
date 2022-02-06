from typing import List

from protocol0.domain.enums.BarLengthEnum import BarLengthEnum
from protocol0.application.faderfox.InterfaceState import InterfaceState
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.recorder.track_recorder_external_synth_mixin import TrackRecorderExternalSynthMixin


class TrackRecorderExternalSynth(TrackRecorderExternalSynthMixin, AbstractTrackRecorder):
    def _arm_track(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(TrackRecorderExternalSynth, self)._arm_track)

        if not self.track.record_clip_tails or InterfaceState.SELECTED_RECORDING_BAR_LENGTH == BarLengthEnum.UNLIMITED:
            if self.track.audio_tail_track:
                seq.add(self.track.audio_tail_track.unarm)

        return seq.done()

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.midi_track, self.track.audio_track, self.track.audio_tail_track])
