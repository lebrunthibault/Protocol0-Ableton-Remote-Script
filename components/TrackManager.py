from __future__ import with_statement

import Live
from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.AutomationTrack import AutomationTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer


class TrackManager(AbstractControlSurfaceComponent):
    def on_selected_track_changed(self):
        if self.song.tracks_added:
            self.song.tracks_added = False
            self._configure_added_track(self.song.current_track)

    @defer
    def _configure_added_track(self, current_track):
        # type: (AbstractTrack) -> None
        current_track.action_arm()
        [clip.delete() for clip in current_track.all_clips]
        [TrackName(track).set(clip_slot_index=0) for track in current_track.all_tracks]
        arp = find_if(lambda d: d.name.lower() == "arpeggiator rack", current_track.all_devices)
        if arp:
            chain_selector_param = find_if(lambda d: d.name.lower() == "chain selector", arp.parameters)
            if chain_selector_param and chain_selector_param.is_enabled:
                chain_selector_param.value = 0

    @staticmethod
    def create_simple_track(track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        if "automation" in track.name.lower() and track.has_midi_input:
            return AutomationTrack(track=track, index=index)
        else:
            return SimpleTrack(track=track, index=index)



