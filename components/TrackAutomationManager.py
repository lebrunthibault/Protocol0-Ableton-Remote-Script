from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.track.AutomationTrack import AutomationTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import defer
from a_protocol_0.utils.utils import find_last


class TrackAutomationManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    @defer
    def create_automation_group(self, base_track):
        # type: (SimpleTrack) -> None
        """ first step, instrument track is selected """
        self.parent.clyphxBrowserManager.load_from_user_library(None, "'LFOTool_filter_automation.adg'")
        self.parent.trackManager.on_selected_track_changed_callbacks.append(self._create_automation_track)
        self.parent.keyboardShortcutManager.group_track()

    def _create_automation_track(self):
        """ 2nd step, the track is grouped, we insert the midi automation track """
        self.parent.keyboardShortcutManager.show_hide_plugins()
        self.song._song.create_midi_track(self.song.selected_track.index + 1)
        self.parent.trackManager.on_selected_track_changed_callbacks.append(self._setup_automation_track)

    def _setup_automation_track(self):
        """ 3rd and last step, the automation track is selected and we set it up """
        self.song.selected_track._track.name = AUTOMATION_TRACK_NAME
        self.song.selected_track.color = self.song.next_track().color

        def step2():
            self.parent.songManager._tracks_listener()
            track = self.song.selected_track  # type: AutomationTrack
            [track.delete_device(d) for d in track.top_devices]
            track.create_clip(bar_count=1)
            track.output_routing_type = find_if(lambda r: r.display_name == self.song.next_track()._track.name,
                                                track.available_output_routing_types)

            self.parent.defer(step3)

        def step3():
            self.song.selected_track.output_routing_channel = find_last(lambda r: "lfotool" in r.display_name.lower(),
                                                     self.song.selected_track.available_output_routing_channels)
            self.song.selected_track.playable_clip.is_playing = True
            self.parent.push2Manager._update_selected_modes()

        self.parent.defer(step2)
