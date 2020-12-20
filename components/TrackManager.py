from __future__ import with_statement

from typing import List

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.track.AutomationTrack import AutomationTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(TrackManager, self).__init__(*a, **k)
        self.tracks_added = False
        self.automation_track_color = None
        self.on_selected_track_changed_callbacks = []  # type: List[callable]

    def on_selected_track_changed(self):
        [self.parent.defer(callback) for callback in self.on_selected_track_changed_callbacks]
        self.on_selected_track_changed_callbacks = []

    def _configure_added_track(self):
        if self.song.current_track.is_simple_group:
            return
        self.song.current_track.action_arm()
        [clip.delete() for clip in self.song.current_track.all_clips]
        [TrackName(track).set(clip_slot_index=0) for track in self.song.current_track.all_tracks]
        arp = find_if(lambda d: d.name.lower() == "arpeggiator rack", self.song.current_track.all_devices)
        if arp:
            chain_selector_param = find_if(lambda d: d.name.lower() == "chain selector", arp.parameters)
            if chain_selector_param and chain_selector_param.is_enabled:
                chain_selector_param.value = 0

    def create_simple_track(self, track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        if AUTOMATION_TRACK_NAME in track.name and track.has_midi_input:
            return AutomationTrack(track=track, index=index)
        else:
            return SimpleTrack(track=track, index=index)
