from typing import Optional

from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackMonitoringState import \
    ExternalSynthTrackMonitoringState
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrackArmState(object):
    def __init__(self, base_track, midi_track, monitoring_state):
        # type: (SimpleTrack, SimpleMidiTrack, ExternalSynthTrackMonitoringState) -> None
        self._base_track = base_track
        self._sub_tracks = base_track.sub_tracks
        self._midi_track = midi_track
        self._monitoring_state = monitoring_state

    @property
    def is_armed(self):
        # type: () -> bool
        return all(sub_track.is_armed for sub_track in self._sub_tracks if not isinstance(sub_track, SimpleDummyTrack))

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        for track in self._sub_tracks:
            if not isinstance(track, SimpleDummyTrack):
                track.is_armed = is_armed

    @property
    def is_partially_armed(self):
        # type: () -> bool
        return any(sub_track.is_armed for sub_track in self._sub_tracks if not isinstance(sub_track, SimpleDummyTrack))

    def arm_track(self):
        # type: () -> Optional[Sequence]
        self._base_track.is_folded = False
        self._base_track.muted = False

        if SongFacade.usamo_track():
            SongFacade.usamo_track().input_routing.track = self._midi_track
            SongFacade.usamo_device().device_on = True  # this is the default: overridden by prophet

        self._monitoring_state.monitor_midi()

        seq = Sequence()
        seq.add([sub_track.arm_track for sub_track in self._sub_tracks if not isinstance(sub_track, SimpleDummyTrack)])
        return seq.done()

    def unarm(self):
        # type: () -> None
        self.is_armed = False
        self._monitoring_state.monitor_audio()
