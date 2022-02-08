from typing import List, Any

from protocol0.domain.audit.SetUpgradeService import SetUpgradeService
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.StatusBar import StatusBar


class SetFixerService(object):
    def __init__(self, validator_service, set_upgrade_service, song):
        # type: (ValidatorService, SetUpgradeService, Song) -> None
        self._validator_service = validator_service
        self._set_upgrade_service = set_upgrade_service
        self._song = song

    def fix(self):
        # type: () -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""
        Logger.clear()

        for obj in self._objects_to_refresh_appearance:
            if hasattr(obj, "refresh_appearance"):
                obj.refresh_appearance()

        invalid_objects = []

        for obj in self._objects_to_validate:
            is_valid = self._validator_service.validate_object(obj)
            if not is_valid:
                invalid_objects.append(obj)

        devices_to_remove = list(self._set_upgrade_service.get_deletable_devices(full_scan=True))

        if len(invalid_objects) == 0 and len(devices_to_remove) == 0:
            StatusBar.show_message("Set is valid")
        else:
            message = "Invalid set."
            if len(invalid_objects):
                message += " Invalid objects: %s." % (len(invalid_objects))
                Logger.log_warning("invalid_objects: %s" % invalid_objects)
            if len(devices_to_remove):
                message += " devices to remove: %s." % (len(devices_to_remove))
            StatusBar.show_message(message)
            Logger.log_warning("devices_to_remove: %s" % [(d, d.track) for d in devices_to_remove])

    @property
    def _objects_to_validate(self):
        # type: () -> List[Any]
        # noinspection PyTypeChecker
        return list(self._song.abstract_tracks) + [self._song]

    @property
    def _objects_to_refresh_appearance(self):
        # type: () -> List[Any]
        # noinspection PyTypeChecker
        return [clip for track in SongFacade.simple_tracks() for clip in track.clips] + \
               SongFacade.scenes() + \
               list(SongFacade.all_simple_tracks())
