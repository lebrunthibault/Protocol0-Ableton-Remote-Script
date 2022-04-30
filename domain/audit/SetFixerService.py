from typing import List, Any

from protocol0.domain.audit.SetUpgradeService import SetUpgradeService
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class SetFixerService(object):
    def __init__(self, validator_service, set_upgrade_service, song):
        # type: (ValidatorService, SetUpgradeService, Song) -> None
        self._validator_service = validator_service
        self._set_upgrade_service = set_upgrade_service
        self._song = song

    @property
    def _objects_to_refresh_appearance(self):
        # type: () -> List[Any]
        # noinspection PyTypeChecker
        return [clip for track in SongFacade.simple_tracks() for clip in track.clips] + \
               SongFacade.scenes() + \
               list(SongFacade.abstract_tracks())

    def refresh_appearance(self):
        # type: () -> None
        for obj in self._objects_to_refresh_appearance:
            if hasattr(obj, "refresh_appearance"):
                obj.refresh_appearance()

    @property
    def _objects_to_validate(self):
        # type: () -> List[Any]
        # noinspection PyTypeChecker
        return [self._song] + SongFacade.scenes() + list(SongFacade.abstract_tracks())

    def fix_set(self):
        # type: () -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""
        Logger.clear()

        invalid_objects = []

        for obj in self._objects_to_validate:
            is_valid = self._validator_service.validate_object(obj)
            if not is_valid:
                invalid_objects.append(obj)

        devices_to_remove = list(self._set_upgrade_service.get_deletable_devices(full_scan=True))

        if len(invalid_objects) == 0 and len(devices_to_remove) == 0:
            Backend.client().show_success("Set is valid")
            self.refresh_appearance()
        else:
            if len(invalid_objects):
                first_object = invalid_objects[0]
                if isinstance(first_object, AbstractTrack):
                    first_object.select()
            if len(devices_to_remove):
                Logger.warning("Devices to remove: %s" % devices_to_remove)
            Backend.client().show_warning("Invalid set: fixing")
            for invalid_object in invalid_objects:
                self._validator_service.fix_object(invalid_object)
            Logger.info("set fixed")
