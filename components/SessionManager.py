from typing import Optional, Any, List

from _Framework.SessionComponent import SessionComponent
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SessionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SessionManager, self).__init__(*a, **k)
        self.session = None  # type: Optional[SessionComponent]
        # self.register_slot(self.parent.songManager, self._setup_session_control, "selected_track")
        self._currently_selected_track = None  # type: Optional[SimpleTrack]

    def _setup_session_control(self):
        # type: () -> None
        if self._currently_selected_track == self.song.selected_track:
            return None
        is_set_load = self._currently_selected_track is None
        self._currently_selected_track = self.song.selected_track
        if is_set_load and not self._currently_selected_track.abstract_track.is_armed:  # skips the session box display on set load
            return
        if self.session:
            self.session.set_show_highlight(False)
            self.session.disconnect()

        try:
            if not self.song.selected_track.is_active:
                return
        except IndexError:
            return

        def get_all_sub_tracks_inclusive(parent_track):
            # type: (SimpleTrack) -> List[SimpleTrack]
            sub_tracks = [parent_track]
            for sub_track in parent_track.sub_tracks:
                sub_tracks.extend(get_all_sub_tracks_inclusive(sub_track))
            return sub_tracks

        total_tracks = get_all_sub_tracks_inclusive(self.song.current_track.base_track)
        num_tracks = len([track for track in total_tracks if track.is_visible])
        track_offset = self.session_track_offset
        self.parent.log_dev("num_tracks: %s" % num_tracks)
        self.parent.log_dev("self.session_track_offset: %s" % track_offset)
        self.parent.log_dev("len(list(self.song.visible_tracks)): %s" % len(list(self.song.visible_tracks)))

        with self.parent.component_guard():
            self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(self.song.scenes))
        self.session.set_offsets(track_offset=track_offset, scene_offset=0)
        if track_offset != len(list(self.song.visible_tracks)) - 1:
            self.parent.log_dev("no highlight")
            self.parent.set_highlighting_session_component(self.session)

    @property
    def session_track_offset(self):
        # type: () -> int
        try:
            return list(self.song.visible_tracks).index(self.song.current_track.base_track)
        except ValueError:
            return self.session.track_offset() if self.session else 0
