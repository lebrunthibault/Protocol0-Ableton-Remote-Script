from typing import List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SongStateManager(AbstractControlSurfaceComponent):
    def sync_simple_tracks_state(self, former_simple_tracks, new_simple_tracks):
        # type: (List[SimpleTrack], List[SimpleTrack]) -> None
        current_simple_tracks_by_live_id = {track.live_id: track for track in new_simple_tracks}
        for former_simple_track in former_simple_tracks:
            if former_simple_track.live_id in current_simple_tracks_by_live_id:
                self._sync_simple_track(former_simple_track, current_simple_tracks_by_live_id[former_simple_track.live_id])

    def _sync_simple_track(self, former_simple_track, new_simple_track):
        # type: (SimpleTrack, SimpleTrack) -> None
        if former_simple_track.instrument and new_simple_track.instrument:
            new_simple_track.instrument.activated = former_simple_track.instrument.activated
            if former_simple_track.instrument.active_instance == former_simple_track.instrument:
                new_simple_track.instrument.active_instance = new_simple_track.instrument
        # automation tracks
        if hasattr(former_simple_track, "automated_parameter"):
            new_simple_track.automated_parameter = former_simple_track.automated_parameter



