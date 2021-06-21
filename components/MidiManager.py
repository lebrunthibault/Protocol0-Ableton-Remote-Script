import json
import time
from functools import partial

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import MIDI_STATUS_BYTES
from typing import Optional, Tuple


class MidiManager(AbstractControlSurfaceComponent):
    START_AT = None

    @staticmethod
    def string_to_sysex(message):
        # type: (str) -> Tuple
        b = bytearray(message.encode())
        b.insert(0, 0xF0)
        b.append(0xF7)
        return tuple(b)

    @staticmethod
    def sysex_to_string(sysex):
        # type: (Tuple) -> str
        return bytearray(sysex[1:-1]).decode()

    def send_program_change(self, value, channel=0):
        # type: (int, int) -> None
        self._send_formatted_midi_message("pc", channel, value)

    def send_string(self, message):
        # type: (str) -> None
        self.START_AT = time.time()
        self.parent.log_dev("Sending string to midi output : %s" % message)
        b = bytearray(message.encode())
        b.insert(0, 0xF0)
        b.append(0xF7)
        self.parent._send_midi(tuple(b))

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

    def receive_midi(self, midi_bytes):
        # type: (Tuple) -> None
        message = self.sysex_to_string(sysex=midi_bytes)
        try:
            obj = json.loads(message)
        except ValueError:
            self.parent.log_error("json decode error on string : %s, bytes: %s" % (message, midi_bytes))
            return

        self.parent.log_dev("P0 received object from sysex: %s" % obj)
        self.parent.log_dev("took %s" % (time.time() - self.START_AT))
        self.parent.apiManager.execute_action_from_api(obj)
