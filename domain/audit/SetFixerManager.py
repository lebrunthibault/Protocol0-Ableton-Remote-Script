from typing import List

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.lom.AbstractObject import AbstractObject


class SetFixerManager(AbstractControlSurfaceComponent):
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
            self.parent.show_message("Set is valid")
        else:
            message = "Invalid set."
            if len(invalid_objects):
                message += " Invalid objects: %s." % (len(invalid_objects))
                self.parent.log_warning("invalid_objects: %s" % invalid_objects)
            if len(devices_to_remove):
                message += " devices to remove: %s." % (len(devices_to_remove))
            self.parent.show_message(message)
            self.parent.log_warning("devices_to_remove: %s" % [(d, d.track) for d in devices_to_remove])

    @property
    def _objects_to_validate(self):
        # type: () -> List[AbstractObject]
        # noinspection PyTypeChecker
        return list(self.song.abstract_tracks) + [self.song]

    @property
    def _objects_to_refresh_appearance(self):
        # type: () -> List[AbstractObject]
        # noinspection PyTypeChecker
        return [clip for track in self.song.simple_tracks for clip in track.clips] + \
               self.song.scenes + \
               list(self.song.all_simple_tracks)
