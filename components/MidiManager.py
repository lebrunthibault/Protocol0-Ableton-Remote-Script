from functools import partial
from typing import Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import MIDI_STATUS_BYTES
from a_protocol_0.utils.utils import parse_midi_channel, parse_midi_value


class MidiManager(AbstractControlSurfaceComponent):
    def send_program_change(self, value, channel=0):
        # type: (int, Optional[int]) -> None
        self._send_formatted_midi_message("pc", channel, value)

    def send_control_change_absolute(self, cc_number, channel=0):
        # type: (int, Optional[int]) -> None
        self.send_control_change(cc_number, 0, channel)
        self.parent.defer(lambda: self.parent.midiManager.send_control_change(cc_number, 127, channel))

    def send_control_change(self, cc_number, value=127, channel=0):
        # type: (int, Optional[int], Optional[int]) -> None
        self._send_formatted_midi_message("cc", channel, cc_number, value)

    def _send_formatted_midi_message(self, message_type, channel, value, value2=None):
        # type: (str, int, int, Optional[int]) -> None
        status = MIDI_STATUS_BYTES[message_type]
        status += parse_midi_channel(channel)
        msg = [status, parse_midi_value(value)]
        if value2:
            msg.append(value2)
        self.parent.log_info("MidiManager sending : %s" % msg)
        self.parent._send_midi(tuple(msg))
        if message_type == 'note':
            msg[-1] = 0
            self.canonical_parent.schedule_message(1, partial(self.parent._send_midi, tuple(msg)))
