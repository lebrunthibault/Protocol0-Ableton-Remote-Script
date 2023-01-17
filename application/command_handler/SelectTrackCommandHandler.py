from protocol0.application.command.SelectTrackCommand import SelectTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song


class SelectTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (SelectTrackCommand) -> None
        track = find_if(lambda t: t.name == command.track_name, Song.simple_tracks())

        assert track is not None, "Couldn't find track %s" % command.track_name
        track.select()
