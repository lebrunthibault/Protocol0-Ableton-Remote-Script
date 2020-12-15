from __future__ import with_statement

from _Framework.SessionComponent import SessionComponent
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.decorators import catch_and_log


class SessionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(SessionManager, self).__init__(is_enabled=False, *a, **k)
        self.session = None

    @property
    def session_track_offset(self):
        # type: () -> int
        return [t for t in self.song.tracks if t.is_visible].index(self.song.current_track.base_track)

    @catch_and_log
    def _setup_session_control(self):
        if not self.is_enabled() or self.song.current_track is None:
            return
        if self.session:
            self.session.disconnect()
        num_tracks = len([track for track in self.song.current_track.all_tracks if track.is_visible])
        self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(self.song.scenes))
        self.session.set_offsets(track_offset=self.session_track_offset, scene_offset=0)
        self.parent.set_highlighting_session_component(self.session)

    def on_selected_track_changed(self):
        self._setup_session_control()

    def on_scene_list_changed(self):
        self._setup_session_control()

