from typing import List

from protocol0.devices.InstrumentProphet import InstrumentProphet
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.track_recorder.recorder.abstract_track_recorder_external_synth import AbstractTrackRecorderExternalSynth


class TrackRecorderExternalSynth(AbstractTrackRecorderExternalSynth):
    def _pre_record(self):
        # type: () -> None
        self.track.solo = False
        self.track.midi_track.select()
        self.parent.navigationManager.show_device_view()
        if isinstance(self.track.instrument, InstrumentProphet) and not InstrumentProphet.EDITOR_DEVICE_ON:
            self.parent.defer(self.system.show_plugins)

    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.midi_track, self.track.audio_track, self.track.audio_tail_track])
