from protocol0.application.command.LoadDrumRackCommand import LoadDrumRackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.shared.sequence.Sequence import Sequence


class LoadDrumRackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (LoadDrumRackCommand) -> Sequence
        return self._container.get(TrackFactory).add_drum_track(
            command.drum_name, DeviceEnum.DRUM_RACK
        )
