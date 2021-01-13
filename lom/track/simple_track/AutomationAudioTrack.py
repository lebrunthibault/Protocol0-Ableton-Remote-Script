from functools import partial

from typing import List

from _Framework.Util import find_if
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class AutomationAudioTrack(SimpleTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationAudioTrack, self).__init__(*a, **k)
        self.clip_slots = self.clip_slots  # type: List[AutomationAudioClipSlot]
        self.automated_device = None  # type: Device
        self.automated_parameter = None  # type: DeviceParameter
        self._get_automated_device_and_parameter()

    def _added_track_init(self):
        if self.group_track is None:
            raise Protocol0Error("An automation track should always be grouped")

        self.has_monitor_in = True
        seq = Sequence()
        seq.add(wait=1)
        seq.add(partial(self.parent.browserManager.load_rack_device, self.name.split(":")[1]))
        seq.add(self._get_automated_device_and_parameter)

        return seq.done()

    def _get_automated_device_and_parameter(self):
        [_, device_name, parameter_name] = self.name.split(":")
        automated_device = find_if(lambda d: d.name == device_name, self.devices)
        if automated_device:
            self.automated_device = automated_device
            self.automated_parameter = find_if(lambda p: p.name == parameter_name, self.automated_device.parameters)

    def automate_from_note(self, parameter, notes):
        # type: (DeviceParameter, List[Note]) -> None
        envelope = self.playable_clip.create_automation_envelope(parameter)
        self.parent.log_debug(envelope)
        for note in notes:
            envelope.insert_step(note.start, note.duration, note.velocity)
