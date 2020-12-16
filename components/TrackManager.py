from __future__ import with_statement

import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.AutomationTrack import AutomationTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer
from a_protocol_0.utils.utils import find_last


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(TrackManager, self).__init__(*a, **k)
        self.tracks_added = False
        self.automation_track_added = False
        self.automation_track_color = None
        self.select_next_track = False

    def on_selected_track_changed(self):
        if self.tracks_added:
            self.tracks_added = False
            self._configure_added_track(self.song.current_track)
            if self.select_next_track:
                self.select_next_track = False
                self.parent.defer(lambda: self.song.select_track(self.song.tracks[self.song.selected_track.index + 1]))
                self.parent._wait(2, lambda: setattr(self.parent.push2Manager.push2._grid_resolution, "index", 5))
        if self.automation_track_added:
            self.automation_track_added = False
            self._set_up_lfo_tool_automation_group_track(self.song.current_track.base_track)

    @defer
    def _configure_added_track(self, current_track):
        # type: (AbstractTrack) -> None
        if current_track.is_simple_group:
            return
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

    def set_up_lfo_tool_automation(self, base_track):
        # type: (SimpleTrack) -> None
        self.parent.clyphxBrowserManager.load_from_user_library(None, "'LFOTool_filter_automation.adg'")

        def finish_setup():
            self.parent.keyboardShortcutManager.show_hide_plugins()
            self.parent.clyphxGlobalManager.add_midi_track(None, base_track.index + 1)
            self.automation_track_color = base_track.color
            self.automation_track_added = True

        self.parent._wait(3, finish_setup)

    @defer
    def _set_up_lfo_tool_automation_group_track(self, base_track):
        # type: (SimpleTrack) -> None
        self.parent.clyphxNavigationManager._app_view.is_view_visible('Session')
        self.parent.clyphxNavigationManager.focus_main()
        base_track.name = "automation"
        base_track.color = self.automation_track_color
        base_track = self.song.tracks[base_track.index] = AutomationTrack(track=base_track._track,
                                                                          index=base_track.index)
        base_track.fill_notes.subject = base_track.clip_slots[0]._clip_slot
        base_track.delete_device(base_track.top_devices[0])
        base_track.create_clip(bar_count=1)
        base_track.output_routing_type = find_if(lambda r: r.display_name == self.song.next_track(base_track).name,
                                                 base_track.available_output_routing_types)

        def finish_setup():
            base_track.output_routing_channel = find_last(lambda r: "LFOtool".lower() in r.display_name.lower(),
                                                          base_track.available_output_routing_channels)
            self.song.highlighted_clip_slot = base_track.clip_slots[0]
            base_track.playable_clip.is_playing = True
            self.select_next_track = True
            self.parent.push2Manager.update_highlighted_clip = False
            self.parent.keyboardShortcutManager.group_adjacent_track()
        self.parent._wait(2, finish_setup)

