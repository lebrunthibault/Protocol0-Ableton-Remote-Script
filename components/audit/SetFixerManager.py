from typing import List

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.AbstractObject import AbstractObject


class SetFixerManager(AbstractControlSurfaceComponent):
    def fix(self):
        # type: () -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""
        self.parent.logManager.clear()
        for obj in self._objects_to_validate:
            self.parent.validatorManager.validate_object(obj)

        for obj in self._objects_to_refresh_appearance:
            obj.refresh_appearance()

        self.parent.show_message("Set fixed")

    @property
    def _objects_to_validate(self):
        # type: () -> List[AbstractObject]
        return list(self.song.abstract_tracks) + list(self.song.simple_tracks)

    @property
    def _objects_to_refresh_appearance(self):
        # type: () -> List[AbstractObject]
        # noinspection PyTypeChecker
        return [clip for track in self.song.simple_tracks for clip in track.clips] + self.song.scenes
