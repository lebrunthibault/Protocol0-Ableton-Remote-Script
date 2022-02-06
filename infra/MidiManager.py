from typing import Optional, Tuple, Type, Callable

from _Framework.ControlSurface import get_control_surfaces
from protocol0.domain.CommandBusInterface import CommandBusInterface
from protocol0.domain.shared.utils import find_if
from protocol0.infra.System import System
from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.infra.scheduler.SchedulerEvent import SchedulerEvent
from protocol0.shared.Logger import Logger


class MidiManager(object):
    _MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}

    def __init__(self, command_bus, send_midi):
        # type: (Type[CommandBusInterface], Callable) -> None
        self._command_bus = command_bus
        self._send_midi = send_midi
        self.midi_server_check_timeout_scheduler_event = None  # type: Optional[SchedulerEvent]

    def _sysex_to_string(self, sysex):
        # type: (Tuple) -> str
        return bytearray(sysex[1:-1]).decode()

    def send_program_change(self, value, channel=0):
        # type: (int, int) -> None
        self._send_formatted_midi_message("pc", channel, value)

    def _send_formatted_midi_message(self, message_type, channel, value, value2=None):
        # type: (str, int, int, Optional[int]) -> None
        status = self._MIDI_STATUS_BYTES[message_type]
        assert 0 <= channel <= 15
        assert 0 <= value <= 127
        status += channel
        msg = [status, value]
        if value2:
            msg.append(value2)
        Logger.log_info("MidiManager sending : %s" % msg, debug=False)
        self._send_midi(tuple(msg))

    def receive_midi(self, midi_bytes):
        # type: (Tuple) -> None
        message = self._sysex_to_string(sysex=midi_bytes)
        Logger.log_debug("message: %s" % message)
        if not self._command_bus:
            Logger.log_warning("Command bus not set in Midi Manager")
            return None

        self._command_bus.execute_from_string(message)

    def ping_midi_server(self):
        # type: () -> None
        self._check_midi_server_is_running()
        Scheduler.wait(10, self._check_protocol_midi_is_up)  # waiting for Protocol0_midi to boot

    def _check_midi_server_is_running(self):
        # type: () -> None
        self.MIDI_SERVER_CHECK_TIMEOUT_SCHEDULER_EVENT = Scheduler.wait(300, self._no_midi_server_found)
        System.get_instance().ping()

    def _check_protocol_midi_is_up(self):
        # type: () -> None
        from protocol0_midi import Protocol0Midi
        protocol0_midi = find_if(lambda cs: isinstance(cs, Protocol0Midi), get_control_surfaces())
        if protocol0_midi is None:
            Logger.log_error("Protocol0Midi is not loaded")

    def _no_midi_server_found(self):
        # type: () -> None
        Logger.log_warning("Midi server is not running.")
