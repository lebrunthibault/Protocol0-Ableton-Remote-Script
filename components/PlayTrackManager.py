from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.PlayMenuEnum import PlayMenuEnum


class PlayTrackManager(AbstractControlSurfaceComponent):
    def action_solo_play_selected_tracks(self):
        if not self.song.has_solo_selection:
            self.song.solo_stopped_tracks = [t for t in self.song.abstract_tracks if t.is_playing and not any(
                t == selected_track or selected_track.is_parent(t) for selected_track in self.song.selected_abstract_tracks)]
            [t.stop() for t in self.song.solo_stopped_tracks]
            self.song.selected_track_category = PlayMenuEnum.RESTART_SOLO_STOPPED
        self.song.solo_playing_tracks += self.song.selected_abstract_tracks
        [t.play() for t in self.song.solo_playing_tracks]

    def handle_play_menu_click(self):
        if self.song.selected_track_category == PlayMenuEnum.RESTART_SOLO_STOPPED:
            [t.play() for t in self.song.solo_stopped_tracks]
            self.song.solo_stopped_tracks = self.song.solo_playing_tracks = []
        elif self.song.selected_track_category == PlayMenuEnum.RESET_SOLO_PLAY:
            self.parent.show_message("Solo play reset")
            self.song.solo_stopped_tracks = self.song.solo_playing_tracks = []
