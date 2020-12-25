from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.track.AutomationTrack import AutomationTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer, wait
from a_protocol_0.utils.utils import find_last


class TrackAutomationManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    @defer
    def create_automation_group(self, base_track):
        # type: (SimpleTrack) -> None
        """ first step, instrument track is selected """
        self.parent.browserManager.load_rack_device("LFOTool_filter_automation")
        self.parent.defer(self.parent.keyboardShortcutManager.show_hide_plugins)
        self.parent.defer(self.parent.keyboardShortcutManager.group_track)
        self.parent.trackManager._added_track_listener._callbacks.append(self._create_automation_track)

    def _create_automation_track(self):
        """ 2nd step, the track is grouped, we insert the midi automation track """
        self.song._song.create_midi_track(self.song.selected_track.index + 1)
        self.parent.trackManager._added_track_listener._callbacks.append(self._setup_automation_track)

    @defer
    def _setup_automation_track(self):
        """ 3rd and last step, the automation track is selected and we set it up """
        TrackName(self.song.selected_track).name = AUTOMATION_TRACK_NAME
        self.song.selected_track.color = self.song.next_track().color
        self.step2()

    @wait(3)
    def step2(self):
        self.parent.songManager._tracks_listener()  # rebuild tracks
        track = self.song.selected_track  # type: AutomationTrack
        [track.delete_device(d) for d in track.top_devices]
        track.output_routing_type = find_if(lambda r: r.display_name == self.song.next_track()._track.name,
                                            track.available_output_routing_types)
        self.step3()

    @defer
    def step3(self):
        self.song.selected_track.output_routing_channel = find_last(lambda r: "lfotool" in r.display_name.lower(),
                                                                    self.song.selected_track.available_output_routing_channels)
