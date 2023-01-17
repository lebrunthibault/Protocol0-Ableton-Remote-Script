from protocol0.application.command.RecordUnlimitedCommand import (
    RecordUnlimitedCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.shared.Song import Song


class RecordUnlimitedCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (RecordUnlimitedCommand) -> None
        self._container.get(RecordService).record_track(
            Song.current_track(), RecordTypeEnum.MIDI_UNLIMITED
        )
