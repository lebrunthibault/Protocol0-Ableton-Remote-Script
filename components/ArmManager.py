from __future__ import with_statement

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class ArmManager(AbstractControlSurfaceComponent):
    def on_selected_track_changed(self):
        if self.song.tracks_added:
            self.parent.defer(self.current_track.action_arm)
            self.song.tracks_added = False

