from typing import Optional, Tuple, Callable

from _Framework.ControlSurface import get_control_surfaces
from protocol0.application.CommandBus import CommandBus
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import PresetProgramSelectedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.System import System
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.scheduler.SchedulerEvent import SchedulerEvent
from protocol0.domain.shared.utils import find_if
from protocol0.infra.midi.MidiBytesReceivedEvent import MidiBytesReceivedEvent
from protocol0.shared.logging.Logger import Logger


class MidiService(object):
    _MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}

    def __init__(self, send_midi):
        # type: (Callable) -> None
        self._send_midi = send_midi
        self._midi_server_check_timeout_scheduler_event = None  # type: Optional[SchedulerEvent]

        DomainEventBus.subscribe(MidiBytesReceivedEvent, self._on_midi_bytes_received_event)
        DomainEventBus.subscribe(PresetProgramSelectedEvent, self._on_preset_program_selected_event)
        self._ping_midi_server()

    def _sysex_to_string(self, sysex):
        # type: (Tuple) -> str
        return bytearray(sysex[1:-1]).decode()

    def _send_program_change(self, value, channel=0):
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
        Logger.log_info("MidiService sending : %s" % msg, debug=False)
        self._send_midi(tuple(msg))

    def _on_midi_bytes_received_event(self, event):
        # type: (MidiBytesReceivedEvent) -> None
        message = self._sysex_to_string(sysex=event.midi_bytes)
        Logger.log_debug("message: %s" % message)
        CommandBus.execute_from_string(message)

    def _on_preset_program_selected_event(self, event):
        # type: (PresetProgramSelectedEvent) -> None
        self._send_program_change(event.preset_index)

    def _ping_midi_server(self):
        # type: () -> None
        self._midi_server_check_timeout_scheduler_event = Scheduler.wait(300, self._no_midi_server_found)
        System.client().ping()
        Scheduler.wait(10, self._check_protocol_midi_is_up)  # waiting for Protocol0_midi to boot

    def pong_from_midi_server(self):
        # type: () -> None
        self._midi_server_check_timeout_scheduler_event.cancel()
        self._midi_server_check_timeout_scheduler_event = None
        Logger.clear()

    def _check_protocol_midi_is_up(self):
        # type: () -> None
        from protocol0_midi import Protocol0Midi
        protocol0_midi = find_if(lambda cs: isinstance(cs, Protocol0Midi), get_control_surfaces())
        if protocol0_midi is None:
            Logger.log_error("Protocol0Midi is not loaded")

    def _no_midi_server_found(self):
        # type: () -> None
        Logger.log_warning("Midi server is not running.")
