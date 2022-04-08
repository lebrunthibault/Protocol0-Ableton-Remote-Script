from typing import TYPE_CHECKING, Tuple

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


class SceneWindow(object):
    def __init__(self, start_length, end_length, contains_scene_end):
        # type: (float, float, bool) -> None
        self._start_length = start_length
        self._end_length = end_length
        self._length = end_length - start_length
        self._contains_scene_end = contains_scene_end

    def __repr__(self):
        # type: () -> str
        return "start: %s, end: %s, contains_scene_end: %s" % (self._start_length, self._end_length, self._contains_scene_end)

    def apply_to_scene(self, scene):
        # type: (Scene) -> None
        for clip in scene.clips:
            if clip.length <= self._length:
                continue

            clip.loop.end = clip.loop_start + self._end_length
            clip.loop.start += self._start_length

            clip.crop()

        if not self._contains_scene_end:
            for clip in scene.clips.audio_tail_clips:
                clip.delete()

    @classmethod
    def create_from_split(cls, scene, split_bar_length):
        # type: (Scene, int) -> Tuple[SceneWindow, SceneWindow]
        cls._validate_scene(scene, split_bar_length)
        crop_length = SongFacade.signature_numerator() * split_bar_length

        if crop_length > 0:
            return cls._create_from_split_length(scene, crop_length)
        else:
            return cls._create_from_split_length(scene, int(scene.length) + crop_length)

    @classmethod
    def _create_from_split_length(cls, scene, split_length):
        # type: (Scene, int) -> Tuple[SceneWindow, SceneWindow]
        return cls(0, split_length, False), cls(split_length, scene.length, True)

    @classmethod
    def create_from_crop(cls, scene, crop_bar_length):
        # type: (Scene, int) -> SceneWindow
        cls._validate_scene(scene, crop_bar_length)
        crop_length = SongFacade.signature_numerator() * crop_bar_length

        if crop_length > 0:
            return cls(0, crop_length, False)
        else:
            return cls(scene.length + crop_length, scene.length, True)

    @classmethod
    def _validate_scene(cls, scene, split_bar_length):
        # type: (Scene, int) -> None
        assert float(split_bar_length).is_integer()
        if scene.bar_length < 2:
            raise Protocol0Warning("Scene should be at least 2 bars for splitting")
        if scene.bar_length % 2 != 0:
            raise Protocol0Warning("Can only split scene with even bar length")
