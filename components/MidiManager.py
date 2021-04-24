from functools import partial

from typing import Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import MIDI_STATUS_BYTES


class MidiManager(AbstractControlSurfaceComponent):
    def send_program_change(self, value, channel=0):
        # type: (int, int) -> None
        self._send_formatted_midi_message("pc", channel, value)

    def _send_formatted_midi_message(self, message_type, channel, value, value2=None):
        # type: (str, int, int, Optional[int]) -> None
        status = MIDI_STATUS_BYTES[message_type]
        assert 0 <= channel <= 15
        assert 0 <= value <= 127
        status += channel
        msg = [status, value]
        if value2:
            msg.append(value2)
        self.parent.log_info("MidiManager sending : %s" % msg, debug=False)
        self.parent._send_midi(tuple(msg))
        if message_type == "note":
            msg[-1] = 0
            self.canonical_parent.schedule_message(1, partial(self.parent._send_midi, tuple(msg)))
