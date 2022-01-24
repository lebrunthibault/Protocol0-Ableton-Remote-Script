from typing import List

from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.track_recorder.recorder.abstract_track_recorder_external_synth import AbstractTrackRecorderExternalSynth


class TrackRecorderExternalSynth(AbstractTrackRecorderExternalSynth):
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
