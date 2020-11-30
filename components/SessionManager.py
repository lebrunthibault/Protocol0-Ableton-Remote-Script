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
        width = 1 + len([child for child in self.current_track.all_nested_children if child.is_visible])
        self.session = SessionComponent(width, len(self.song.scenes))
        width_offset = self.song.visible_tracks.index(self.current_track.base_track)
        self.session.set_offsets(width_offset, 0)
        self.control_surface.set_highlighting_session_component(self.session)

    def on_selected_track_changed(self):
        self._setup_session_control()

    def on_scene_list_changed(self):
        self._setup_session_control()

