from typing import Optional

from protocol0.application.command.SelectTrackCommand import SelectTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SelectTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (SelectTrackCommand) -> Optional[Sequence]
        track = find_if(lambda t: t.name == command.track_name, SongFacade.simple_tracks())

        assert track is not None, "Couldn't find track %s" % command.track_name

        return track.select()
