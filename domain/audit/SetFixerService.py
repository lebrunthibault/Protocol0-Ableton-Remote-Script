from protocol0.domain.audit.SetUpgradeService import SetUpgradeService
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class SetFixerService(object):
    def __init__(self, validator_service, set_upgrade_service):
        # type: (ValidatorService, SetUpgradeService) -> None
        self._validator_service = validator_service
        self._set_upgrade_service = set_upgrade_service

    def fix_set(self):
        # type: () -> bool
        """Fix the current set to the current standard regarding naming / coloring etc .."""
        Logger.clear()

        invalid_objects = []

        objects_to_validate = Song.scenes() + list(Song.abstract_tracks())  # noqa
        for obj in objects_to_validate:
            is_valid = self._validator_service.validate_object(obj)
            if not is_valid:
                invalid_objects.append(obj)

        if len(invalid_objects) == 0:
            Backend.client().show_success("Set is valid")
            self._refresh_objects_appearance()
            return True
        else:
            Backend.client().show_warning("Invalid set: fixing")
            for invalid_object in invalid_objects:
                self._validator_service.fix_object(invalid_object, log=False)
            Logger.info("set fixed")
            return False

    def find_devices_to_remove(self):
        # type: () -> None
        devices_to_remove = list(self._set_upgrade_service.get_deletable_devices())

        if len(devices_to_remove):
            Logger.warning("Devices to remove: %s" % devices_to_remove)

    def _refresh_objects_appearance(self):
        # type: () -> None
        clip_slots = [cs for track in Song.simple_tracks() for cs in track.clip_slots]
        clips = [clip for track in Song.simple_tracks() for clip in track.clips]
        # noinspection PyTypeChecker
        objects_to_refresh_appearance = (
                clip_slots + clips + Song.scenes()
        )

        for obj in objects_to_refresh_appearance:
            obj.appearance.refresh()

        for track in Song.external_synth_tracks():
            track.midi_track.name = "m"
            track.audio_track.name = "a"
