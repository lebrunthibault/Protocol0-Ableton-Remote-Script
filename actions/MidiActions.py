from functools import partial
from typing import Optional

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Dependency import depends
from a_protocol_0.consts import MIDI_STATUS_BYTES
from a_protocol_0.utils.utils import parse_number, parse_midi_channel, parse_midi_value


class MidiActions(ControlSurfaceComponent):
    """ MidiActions provides MIDI-related methods. """

    @depends(send_midi=None)
    def __init__(self, send_midi=None, *a, **k):
        super(MidiActions, self).__init__(*a, **k)
        self._send_midi = send_midi

    def disconnect(self):
        super(MidiActions, self).disconnect()
        self._send_midi = None

    def send_midi_message(self, args):
        # type: (str) -> None
        """ Sends formatted note/cc/pc message or raw MIDI message. """
        msg_def = args.split()
        msg_def_len = len(msg_def)
        if msg_def_len >= 3 and msg_def[0] in MIDI_STATUS_BYTES:
            self._send_formatted_midi_message(msg_def, msg_def_len)
        else:
            msg = [parse_number(b, default_value=0) for b in msg_def]
            self._send_midi(tuple(msg))

    def send_program_change(self, value, channel=0):
        # type: (int, Optional[int]) -> None
        """ Sends formatted note/cc/pc message or raw MIDI message. """
        self._send_formatted_midi_message("pc", channel, value)

    def send_control_change(self, value, channel=0):
        # type: (int, Optional[int]) -> None
        """ Sends formatted note/cc/pc message or raw MIDI message. """
        self._send_formatted_midi_message("cc", channel, value)

    def _send_formatted_midi_message(self, message_type, channel, value):
        # type: (str, int, int) -> None
        status = MIDI_STATUS_BYTES[message_type]
        status += parse_midi_channel(channel)
        msg = [status, parse_midi_value(value)]
        self.canonical_parent.log_message("%s %d %d" % (message_type, channel, value))
        self._send_midi(tuple(msg))
        if message_type == 'note':
            msg[-1] = 0
            self.canonical_parent.schedule_message(1, partial(self._send_midi, tuple(msg)))
