from typing import TYPE_CHECKING, Tuple

from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


class SceneLengthWindow(object):
    def __init__(self, scene, start_length, end_length):
        # type: (Scene, float, float) -> None
        self._scene_length = scene.length
        self.start_length = start_length
        self.end_length = end_length

    @property
    def length(self):
        # type: () -> float
        return self.end_length - self.start_length

    @property
    def has_scene_end(self):
        # type: () -> bool
        return self.end_length == self._scene_length

    @classmethod
    def create_from_split(cls, scene, split_bar_length):
        # type: (Scene, int) -> Tuple[SceneLengthWindow, SceneLengthWindow]
        split_length = SongFacade().signature_numerator() * split_bar_length

        return cls(0, split_length), cls(split_length, scene.length)

    @classmethod
    def create_from_crop(cls, scene, crop_bar_length):
        # type: (Scene, int) -> SceneLengthWindow
        crop_length = SongFacade().signature_numerator() * crop_bar_length

        if crop_length > 0:
            return cls.create_from_split(scene, crop_bar_length)[0]
        else:
            return SceneLengthWindow(scene, scene.length - crop_length, scene.length)

