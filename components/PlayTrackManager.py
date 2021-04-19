from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.PlayMenuEnum import PlayMenuEnum


class PlayTrackManager(AbstractControlSurfaceComponent):
    def action_solo_play_selected_tracks(self):
        # type: () -> None
        if not self.song.has_solo_selection:
            self.song.solo_stopped_tracks = [
                t
                for t in self.song.abstract_tracks
                if t.is_playing
                and not any(
                    t == selected_track or selected_track.is_parent(t)
                    for selected_track in self.song.selected_abstract_tracks
                )
            ]
            for t in self.song.solo_stopped_tracks:
                t.stop()
            self.song.selected_track_category = PlayMenuEnum.RESTART_SOLO_STOPPED
        self.song.solo_playing_tracks += self.song.selected_abstract_tracks
        for t in self.song.solo_playing_tracks:
            t.play()
