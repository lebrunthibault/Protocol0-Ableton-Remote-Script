from typing import List

from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AutomationAudioTrack(SimpleTrack):
    def automate_from_note(self, parameter, notes):
        # type: (DeviceParameter, List[Note]) -> None
        envelope = self.playable_clip.create_automation_envelope(parameter)
        self.parent.log_debug(envelope)
        for note in notes:
            envelope.insert_step(note.start, note.duration, note.velocity)
