import itertools

from typing import List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SongStateManager(AbstractControlSurfaceComponent):
    def sync_simple_tracks_state(self, former_simple_tracks, current_simple_tracks):
        # type: (List[SimpleTrack], List[SimpleTrack]) -> None
        """ not handling track suppression for now """
        if len(former_simple_tracks) == 0:
            return
        self.parent.songManager._set_current_track()
        index = self.song.selected_track.index
        difference = abs(len(current_simple_tracks) - len(former_simple_tracks))

        # added track
        if len(former_simple_tracks) < len(current_simple_tracks):
            current_simple_tracks = current_simple_tracks[0:index] + current_simple_tracks[index + difference:]
        elif len(former_simple_tracks) > len(current_simple_tracks):
            """ 
                when one or multiple tracks are deleted the right next track is then the selected track 
                except when the last track(s) are deleted (there is no right track) so we need to check for this case
            """
            former = former_simple_tracks[0:index] + former_simple_tracks[index + difference:]
            if self.song.selected_track == self.song.simple_tracks[-1] and not self._are_track_lists_equivalent(former,
                                                                                                              current_simple_tracks):
                former = former_simple_tracks[0:len(current_simple_tracks)]
            former_simple_tracks = former

        if not self._are_track_lists_equivalent(former_simple_tracks, current_simple_tracks):
            self.parent.log_error(
                "An error occurred while syncing instrument activation states, track lists are not equivalent")

        for old_track, new_track in itertools.izip(former_simple_tracks, current_simple_tracks):
            if old_track.instrument and new_track.instrument:
                new_track.instrument.activated = old_track.instrument.activated
                if old_track.instrument.active_instance == old_track.instrument:
                    new_track.instrument.active_instance = new_track.instrument
            # automation tracks
            if hasattr(old_track, "automated_parameter"):
                new_track.automated_parameter = old_track.automated_parameter

    def _are_track_lists_equivalent(self, former_simple_tracks, current_simple_tracks):
        # type: (List[SimpleTrack], List[SimpleTrack]) -> bool
        if len(former_simple_tracks) != len(current_simple_tracks):
            return False

        if any([old_track.name != new_track.name for old_track, new_track in
                itertools.izip(former_simple_tracks, current_simple_tracks)]):
            return False

        return True
