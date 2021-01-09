from functools import partial

from typing import List

from _Framework.Util import find_if
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class AutomationAudioTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AutomationAudioTrack, self).__init__(*a, **k)
        [_, device_name, _] = self.name.split(":")
        self.parent.browserManager.load_rack_device, device_name, sync=False

    def _added_track_init(self):
        if self.group_track is None:
            raise RuntimeError("An automation track should always be grouped")
        [self.delete_device(d) for d in self.devices]
        seq = Sequence(auto_start=True)
        self.is_folded = False
        [_, device_name, _] = self.name.split(":")
        seq.add(partial(self.parent.browserManager.load_rack_device, device_name, sync=False))

        return seq.done()

    def automate_from_note(self, parameter, notes):
        # type: (DeviceParameter, List[Note]) -> None
        envelope = self.playable_clip.create_automation_envelope(parameter)
        self.parent.log_debug(envelope)
        for note in notes:
            envelope.insert_step(note.start, note.duration, note.velocity)
