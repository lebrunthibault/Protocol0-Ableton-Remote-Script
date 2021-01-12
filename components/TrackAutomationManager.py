from functools import partial

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_AUDIO_NAME, AUTOMATION_TRACK_MIDI_NAME
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer


class TrackAutomationManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    @defer
    def create_automation_group(self, parameter):
        # type: (DeviceParameter) -> None
        """ first step, instrument track is selected """
        seq = Sequence()

        if self.song.current_track.is_foldable:
            self.song.current_track.is_folded = False
            seq.add(partial(self.song.select_track, self.song.current_track))
        else:
            seq.add(self.parent.trackManager.group_track)

        seq.add(partial(self.parent.trackManager.create_audio_track, self.song.selected_track.index + 1,
                        name="%s:%s:%s" % (AUTOMATION_TRACK_AUDIO_NAME, parameter.device.name, parameter.name)))
        seq.add(partial(self.parent.trackManager.create_midi_track, self.song.selected_track.index + 2,
                        name="%s:%s:%s" % (AUTOMATION_TRACK_MIDI_NAME, parameter.device.name, parameter.name)))
        seq.done()

    def action_set_up_automation_envelope(self, base_track):
        # type: (SimpleTrack) -> None
        self.parent.log_debug(base_track.selected_device)
        self.parent.log_debug(base_track.selected_device.parameters)
        filter_param = find_if(lambda p: p.name == "F.Cutoff", base_track.selected_device.parameters)
        self.parent.log_debug(filter_param)
        envelope = base_track.playable_clip.create_automation_envelope(filter_param)
        self.parent.log_debug(envelope)
        envelope.insert_step(0, 4, 63)
        envelope.insert_step(4, 4, 53)
