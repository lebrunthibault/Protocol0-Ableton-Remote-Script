from __future__ import with_statement

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.decorators import defer


class ArmManager(AbstractControlSurfaceComponent):
    @defer
    def on_selected_track_changed(self):
        if self.song.tracks_added:
            self.current_track.action_arm()
            self.song.tracks_added = False

