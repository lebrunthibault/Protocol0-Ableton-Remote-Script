from protocol0.application.command.CheckAudioExportValidCommand import CheckAudioExportValidCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class CheckAudioExportValidCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (CheckAudioExportValidCommand) -> None
        sound_id_device = Song.master_track().devices.get_one_from_enum(DeviceEnum.SOUNDID_REFERENCE_PLUGIN)
        if sound_id_device is not None and sound_id_device.is_enabled:
            sound_id_device.is_enabled = False
            Logger.warning("Deactivating SoundID Reference plugin for export")
