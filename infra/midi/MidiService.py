from _Framework.ControlSurface import get_control_surfaces
from typing import Optional, Tuple, Callable

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import PresetProgramSelectedEvent
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.decorators import throttle
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import find_if
from protocol0.infra.midi.MidiBytesReceivedEvent import MidiBytesReceivedEvent
from protocol0.shared.logging.Logger import Logger


class MidiService(object):
    _DEBUG = False
    _MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}

    def __init__(self, send_midi):
        # type: (Callable) -> None
        self._send_midi = send_midi
        self._midi_server_up = False

        DomainEventBus.subscribe(MidiBytesReceivedEvent, self._on_midi_bytes_received_event)
        DomainEventBus.subscribe(PresetProgramSelectedEvent, self._on_preset_program_selected_event)
        DomainEventBus.subscribe(SongInitializedEvent, self._on_song_initialized_event)

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
        Logger.info("MidiService sending : %s" % msg)
        self._send_midi(tuple(msg))

    def _on_midi_bytes_received_event(self, event):
        # type: (MidiBytesReceivedEvent) -> None
        message = self._sysex_to_string(sysex=event.midi_bytes)
        if self._DEBUG:
            Logger.info("message: %s" % message)
        command = SerializableCommand.unserialize(message)
        CommandBus.dispatch(command)

    def _on_preset_program_selected_event(self, event):
        # type: (PresetProgramSelectedEvent) -> None
        self._send_program_change(event.preset_index)

    @throttle(wait_time=50)
    def _on_song_initialized_event(self, _):
        # type: (SongInitializedEvent) -> None
        self._ping_midi_server()
        Scheduler.wait(10, self._check_protocol_midi_is_up)  # waiting for Protocol0_midi to boot
        Scheduler.wait(100, self._midi_server_ping_timeout)

    def _ping_midi_server(self):
        # type: () -> None
        Backend.client().ping()

    def pong_from_midi_server(self):
        # type: () -> None
        Logger.info("Midi server is up")
        if self._midi_server_up:
            raise Protocol0Error("Duplicate pong : midi server is loaded multiple times")
        self._midi_server_up = True

    def _check_protocol_midi_is_up(self):
        # type: () -> None
        from protocol0_midi import Protocol0Midi
        protocol0_midi = find_if(lambda cs: isinstance(cs, Protocol0Midi), get_control_surfaces())
        if protocol0_midi is None:
            Logger.error("Protocol0Midi is not loaded")

    def _midi_server_ping_timeout(self):
        # type: () -> None
        if not self._midi_server_up:
            Logger.warning("Midi server is not running.")
