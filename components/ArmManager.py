from __future__ import with_statement

from typing import TYPE_CHECKING

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


class ArmManager(AbstractControlSurfaceComponent):
    def on_selected_track_changed(self):
        if self.song.tracks_added:
            self.parent.defer(self.current_track.action_arm)
            self.song.tracks_added = False

