from typing import List

from protocol0.errors.Protocol0Warning import Protocol0Warning
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.track_recorder.recorder.abstract_track_recorder_external_synth import AbstractTrackRecorderExternalSynth


class TrackRecorderExternalSynthAudio(AbstractTrackRecorderExternalSynth):
    def _pre_record(self):
        # type: () -> None
        if not self.track.midi_track[self.song.selected_scene.index].clip:
            raise Protocol0Warning("No midi clip selected")

    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.audio_track, self.track.audio_tail_track])
