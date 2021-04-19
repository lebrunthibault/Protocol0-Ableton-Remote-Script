from typing import Optional, Any

from _Framework.SessionComponent import SessionComponent
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class SessionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SessionManager, self).__init__(*a, **k)
        self.session = None  # type: Optional[SessionComponent]
        self.register_slot(self.parent.songManager, self._setup_session_control, "selected_track")
        self.register_slot(self.parent.songManager, self._setup_session_control, "scene_list")

    def _setup_session_control(self):
        # type: () -> None
        if not self.is_enabled() or self.song.current_track is None:
            return
        session_track_offset = self.session_track_offset
        if self.session:
            self.session.disconnect()
        num_tracks = len([track for track in self.song.current_track.all_tracks if track.is_visible])
        with self.parent.component_guard():
            self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(self.song.scenes))
        self.session.set_offsets(track_offset=session_track_offset, scene_offset=0)
        self.parent.set_highlighting_session_component(self.session)

    @property
    def session_track_offset(self):
        # type: () -> int
        try:
            return [t for t in self.song.simple_tracks if t.is_visible].index(self.song.current_track.base_track)
        except ValueError:
            return self.session.track_offset() if self.session else 0
