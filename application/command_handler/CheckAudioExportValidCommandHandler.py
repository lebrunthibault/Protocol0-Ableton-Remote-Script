from protocol0.application.command.CheckAudioExportValidCommand import CheckAudioExportValidCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song


class CheckAudioExportValidCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (CheckAudioExportValidCommand) -> None
        sound_id_device = Song.master_track().devices.get_one_from_enum(DeviceEnum.SOUNDID_REFERENCE_PLUGIN)
        if sound_id_device is not None and sound_id_device.is_enabled:
            Backend.client().show_warning("The SoundID Reference plugin is enabled", centered=True)
