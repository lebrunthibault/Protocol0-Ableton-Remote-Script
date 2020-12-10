from __future__ import with_statement

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer


class ArmManager(AbstractControlSurfaceComponent):
    @defer
    def on_selected_track_changed(self):
        if self.song.tracks_added:
            self._configure_added_track(self.song.current_track)

    def _configure_added_track(self, current_track):
        # type: (AbstractTrack) -> None
        self.song.tracks_added = False
        self.parent.push2Manager.update_session_ring()
        current_track.action_arm()
        [clip.delete() for clip in current_track.clips]
        [TrackName(track).set(clip_slot_index=0) for track in current_track.all_tracks]
        arp = find_if(lambda d: d.name.lower() == "arpeggiator rack", current_track.all_devices)
        if arp:
            chain_selector_param = find_if(lambda d: d.name.lower() == "chain selector", arp.parameters)
            if chain_selector_param:
                chain_selector_param.value = 0



