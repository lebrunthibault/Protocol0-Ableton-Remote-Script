from protocol0.application.command.RecordUnlimitedCommand import (
    RecordUnlimitedCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.TrackRecorderService import TrackRecorderService
from protocol0.shared.SongFacade import SongFacade


class RecordUnlimitedCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (RecordUnlimitedCommand) -> None
        self._container.get(TrackRecorderService).record_track(
            SongFacade.current_track(), RecordTypeEnum.MIDI_UNLIMITED
        )
