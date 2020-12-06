from __future__ import with_statement

from _Framework.SessionComponent import SessionComponent
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class SessionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(SessionManager, self).__init__(*a, **k)
        self.session = None
        self._setup_session_control()

    @property
    def session_track_offset(self):
        # type: () -> int
        return self.song.visible_tracks.index(self.current_track.base_track)

    def _setup_session_control(self):
        if self.session:
            self.session.disconnect()
        num_tracks = len([track for track in self.current_track.all_tracks if track.is_visible])
        self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(self.song.scenes))
        self.session.set_offsets(track_offset=self.session_track_offset, scene_offset=0)
        self.parent.set_highlighting_session_component(self.session)

    def on_selected_track_changed(self):
        self._setup_session_control()

    def on_scene_list_changed(self):
        self._setup_session_control()

