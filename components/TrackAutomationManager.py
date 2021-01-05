from functools import partial

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer


class TrackAutomationManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    @defer
    def create_automation_group(self, base_track):
        # type: (SimpleTrack) -> None
        """ first step, instrument track is selected """
        seq = Sequence()

        if self.song.current_track.is_foldable:
            self.song.current_track.is_folded = False
            seq.add(partial(self.song.select_track, self.song.current_track))
        else:
            seq.add(self.parent.trackManager.group_track)
        seq.add(partial(self.parent.browserManager.load_rack_device, "LFOTool_filter_automation", sync=False))
        seq.add(partial(self.parent.trackManager.create_midi_track, self.song.selected_track.index + 1, name=AUTOMATION_TRACK_NAME))

        seq.done()()

