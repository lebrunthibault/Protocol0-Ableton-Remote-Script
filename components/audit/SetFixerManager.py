from typing import List

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.AbstractObject import AbstractObject


class SetFixerManager(AbstractControlSurfaceComponent):
    def fix(self):
        # type: () -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""
        self.parent.logManager.clear()

        for obj in self._objects_to_refresh_appearance:
            obj.refresh_appearance()

        if self.song.usamo_track is None:
            self.parent.show_message("Add usamo track")
            return
        if self.song.template_dummy_clip is None:
            self.parent.show_message("Couldn't find template dummy clip")
            return

        invalid_objects = []

        for obj in self._objects_to_validate:
            is_valid = self.parent.validatorManager.validate_object(obj)
            if not is_valid:
                invalid_objects.append(obj)

        if len(invalid_objects) == 0:
            self.parent.show_message("Set is valid")
        else:
            self.parent.show_message("%s invalid objects in set" % (len(invalid_objects)))

    @property
    def _objects_to_validate(self):
        # type: () -> List[AbstractObject]
        return list(self.song.abstract_tracks)

    @property
    def _objects_to_refresh_appearance(self):
        # type: () -> List[AbstractObject]
        # noinspection PyTypeChecker
        return [clip for track in self.song.simple_tracks for clip in track.clips] + self.song.scenes + list(
            self.song.abstract_tracks)
