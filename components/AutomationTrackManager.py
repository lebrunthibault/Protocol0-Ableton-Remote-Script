import Live

from functools import partial

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer


class AutomationTrackManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    @defer
    def create_automation_group(self, parameter):
        # type: (DeviceParameter) -> None
        """ first step, instrument track is selected """
        seq = Sequence()
        self.parent.songManager.abstract_group_track_creation_in_progress = True

        if self.song.current_track.is_foldable:
            seq.add(lambda: setattr(self.song.current_track, "is_folded", False))
        else:
            seq.add(self.parent.trackManager.group_track)

        if isinstance(parameter.canonical_parent, Live.Device.Device):
            device_type = "d"
        elif isinstance(parameter.canonical_parent, Live.RackDevice.RackDevice):
            device_type = "r"
        else:
            raise RuntimeError("Devices of type %s are not handled" % type(parameter.canonical_parent))
        # this cannot be parallelized
        seq.add(partial(self.parent.trackManager.create_audio_track, self.song.current_track.index + 1,
                        name="%s:%s:%s:%s" % (AUTOMATION_TRACK_NAME, device_type, parameter.device.name, parameter.name)))
        seq.add(partial(self.parent.trackManager.create_midi_track, self.song.current_track.index + 2,
                        name="%s:%s:%s:%s" % (AUTOMATION_TRACK_NAME, device_type, parameter.device.name, parameter.name)))
        seq.add(lambda: setattr(self.parent.songManager, "abstract_group_track_creation_in_progress", False))
        seq.add(wait=1)
        seq.add(self.parent.songManager._tracks_listener)

        return seq.done()
