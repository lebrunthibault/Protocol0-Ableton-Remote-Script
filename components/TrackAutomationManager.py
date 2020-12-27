from functools import partial

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import defer


class TrackAutomationManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    @defer
    def create_automation_group(self, base_track):
        # type: (SimpleTrack) -> None
        """ first step, instrument track is selected """
        if self.song.current_track.is_foldable:
            self.song.select_track(self.song.current_track)
            self.song.current_track.is_folded = False
            self.parent.songManager.on_selected_track_changed._callbacks.append(partial(self._create_automation_track, forward_routing=False))
        else:
            self.parent.trackManager.group_track(callback=self._create_automation_track)

    def _create_automation_track(self, forward_routing=True):
        """ 2nd step, the track is grouped, we insert the midi automation track """
        self.parent.browserManager.load_rack_device("LFOTool_filter_automation")
        group_track = self.song.selected_track

        if forward_routing:
            wrapped_track = self.song.next_track()
            group_track.output_routing_type = find_if(lambda r: r.attached_object == wrapped_track.output_routing_type.attached_object,
                                                      group_track.available_output_routing_types)
            wrapped_track.output_routing_type = find_if(lambda r: r.display_name == group_track._track.name,
                                                        wrapped_track.available_output_routing_types)
        self.parent.trackManager.create_midi_track(group_track.index + 1, name=AUTOMATION_TRACK_NAME)

        self.parent._wait(6, self.song.end_undo_step)