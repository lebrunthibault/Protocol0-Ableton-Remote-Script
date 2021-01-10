from functools import partial

from typing import List

from _Framework.Util import find_if
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class AutomationAudioTrack(SimpleTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationAudioTrack, self).__init__(*a, **k)
        self.automated_device = None  # type: Device
        self.automated_parameter = None  # type: DeviceParameter

    def _added_track_init(self):
        if self.group_track is None:
            raise RuntimeError("An automation track should always be grouped")

        self.automated_parameter = None  # type: DeviceParameter
        self.has_monitor_in = True
        [self.delete_device(d) for d in self.devices]
        seq = Sequence(auto_start=True)
        self.is_folded = False
        [_, device_name, parameter_name] = self.name.split(":")
        seq.add(partial(self.parent.browserManager.load_rack_device, device_name, sync=False))
        seq.add(lambda: setattr(self, "automated_device", find_if(lambda d: d.name == device_name, self.devices)))
        seq.add(lambda: setattr(self, "automated_parameter", find_if(lambda p: p.name == parameter_name, self.automated_device.parameters)))

        return seq.done()

    def automate_from_note(self, parameter, notes):
        # type: (DeviceParameter, List[Note]) -> None
        envelope = self.playable_clip.create_automation_envelope(parameter)
        self.parent.log_debug(envelope)
        for note in notes:
            envelope.insert_step(note.start, note.duration, note.velocity)
