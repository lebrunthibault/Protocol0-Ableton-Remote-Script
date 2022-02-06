from typing import List

from protocol0.shared.AccessContainer import AccessContainer
from protocol0.shared.AccessSong import AccessSong
from protocol0.shared.Logger import Logger
from protocol0.shared.StatusBar import StatusBar


class SetFixerManager(AccessContainer, AccessSong):
    def fix(self):
        # type: () -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""
        self.parent.logManager.clear()

        for obj in self._objects_to_refresh_appearance:
            if hasattr(obj, "refresh_appearance"):
                obj.refresh_appearance()

        invalid_objects = []

        for obj in self._objects_to_validate:
            is_valid = self.parent.validatorManager.validate_object(obj)
            if not is_valid:
                invalid_objects.append(obj)

        devices_to_remove = list(self.parent.setUpgradeManager.get_deletable_devices(full_scan=True))

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
        # type: () -> List[object]
        # noinspection PyTypeChecker
        return list(self.song.abstract_tracks) + [self.song]

    @property
    def _objects_to_refresh_appearance(self):
        # type: () -> List[object]
        # noinspection PyTypeChecker
        return [clip for track in self.song.simple_tracks for clip in track.clips] + \
               self.song.scenes + \
               list(self.song.all_simple_tracks)
