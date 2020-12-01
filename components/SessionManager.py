from __future__ import with_statement

from typing import TYPE_CHECKING

from _Framework.SessionComponent import SessionComponent
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


class SessionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(SessionManager, self).__init__(*a, **k)
        self.session = None

    def _setup_session_control(self):
        if self.session:
            self.session.disconnect()
        num_tracks = 1 + len([child for child in self.current_track.all_nested_children if child.is_visible])
        self.session = SessionComponent(num_tracks=num_tracks, num_scenes=len(self.song.scenes))
        self.session.set_offsets(track_offset=self.song.session_track_offset, scene_offset=0)
        self.control_surface.set_highlighting_session_component(self.session)

    def on_selected_track_changed(self):
        self._setup_session_control()

    def on_scene_list_changed(self):
        self._setup_session_control()

