from typing import Optional, Tuple

from protocol0.application.midi_api.ApiAction import ApiAction
from protocol0.application.midi_api.ApiError import ApiError
from protocol0.shared.Logger import Logger


class MidiManager(object):
    MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}

    @staticmethod
    def _sysex_to_string(sysex):
        # type: (Tuple) -> str
        return bytearray(sysex[1:-1]).decode()

    @classmethod
    def send_program_change(cls, value, channel=0):
        # type: (int, int) -> None
        cls._send_formatted_midi_message("pc", channel, value)

    @classmethod
    def _send_formatted_midi_message(cls, message_type, channel, value, value2=None):
        # type: (str, int, int, Optional[int]) -> None
        status = cls.MIDI_STATUS_BYTES[message_type]
        assert 0 <= channel <= 15
        assert 0 <= value <= 127
        status += channel
        msg = [status, value]
        if value2:
            msg.append(value2)
        Logger.log_info("MidiManager sending : %s" % msg, debug=False)
        from protocol0 import Protocol0
        Protocol0.SELF._send_midi(tuple(msg))

    @classmethod
    def receive_midi(cls, midi_bytes):
        # type: (Tuple) -> None
        message = cls._sysex_to_string(sysex=midi_bytes)
        Logger.log_debug("message: %s" % message)
        try:
            api_action = ApiAction.make_from_string(payload=message)
            Logger.log_debug("api_action: %s" % api_action)
        except ApiError as e:
            Logger.log_error("ApiAction generation error : %s" % e)
            return

        api_action.execute()
