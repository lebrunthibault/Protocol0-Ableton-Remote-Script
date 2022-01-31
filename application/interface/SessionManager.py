from typing import Optional, Any, List

from _Framework.SessionComponent import SessionComponent
from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SessionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SessionManager, self).__init__(*a, **k)
        self.session = None  # type: Optional[SessionComponent]
        # self.register_slot(self.parent.songManager, self.display_session_ring, "selected_track")

    def toggle_session_ring(self):
        # type: () -> None
        self._display_session_ring()
        self._hide_session_ring()

    def _display_session_ring(self):
        # type: () -> None
        if self.session:
            self._hide_session_ring()

        try:
            if not self.song.selected_track.IS_ACTIVE:
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

        with self.parent.component_guard():
            self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(self.song.scenes))
        self.session.set_offsets(track_offset=track_offset, scene_offset=0)
        if track_offset != len(list(self.song.visible_tracks)) - 1:
            self.parent.set_highlighting_session_component(self.session)

    def _hide_session_ring(self):
        # type: () -> None
        if self.session:
            self.session.set_show_highlight(False)
            self.session.disconnect()

    @property
    def session_track_offset(self):
        # type: () -> int
        try:
            return list(self.song.visible_tracks).index(self.song.current_track.base_track)
        except ValueError:
            return self.session.track_offset() if self.session else 0
