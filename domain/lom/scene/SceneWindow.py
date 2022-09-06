from typing import Tuple

from protocol0.domain.lom.clip.DummyClip import DummyClip
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class SceneWindow(object):
    def __init__(self, start_length, end_length, contains_scene_end):
        # type: (float, float, bool) -> None
        self._start_length = start_length
        self._end_length = end_length
        self._length = end_length - start_length
        self._contains_scene_end = contains_scene_end

    def __repr__(self):
        # type: () -> str
        return "start: %s, end: %s, contains_scene_end: %s" % (
            self._start_length,
            self._end_length,
            self._contains_scene_end,
        )

    def apply_to_scene(self, clips):
        # type: (SceneClips) -> None
        Logger.dev("applying %s" % self)
        for clip in clips.all:
            if clip.length <= self._length:
                continue

            if not (self._contains_scene_end and isinstance(clip, DummyClip)):
                clip.loop.end = clip.loop.start + self._end_length
            clip.loop.start += self._start_length

            if not isinstance(clip, DummyClip):
                clip.crop()

        if not self._contains_scene_end:
            for clip in clips.audio_tail_clips:
                clip.delete()

    @classmethod
    def create_from_split(cls, scene_length, split_bar_length):
        # type: (float, int) -> Tuple[SceneWindow, SceneWindow]
        cls._validate_scene(scene_length, split_bar_length)
        crop_length = SongFacade.signature_numerator() * split_bar_length

        if crop_length > 0:
            return cls._create_from_split_length(scene_length, crop_length)
        else:
            return cls._create_from_split_length(scene_length, int(scene_length) + crop_length)

    @classmethod
    def _create_from_split_length(cls, scene_length, split_length):
        # type: (float, int) -> Tuple[SceneWindow, SceneWindow]
        return cls(0, split_length, False), cls(split_length, scene_length, True)

    @classmethod
    def create_from_crop(cls, scene_length, crop_bar_length):
        # type: (float, int) -> SceneWindow
        cls._validate_scene(scene_length, crop_bar_length)
        crop_length = SongFacade.signature_numerator() * crop_bar_length

        if crop_length > 0:
            return cls(0, crop_length, False)
        else:
            return cls(scene_length + crop_length, scene_length, True)

    @classmethod
    def _validate_scene(cls, scene_length, split_bar_length):
        # type: (float, int) -> None
        bar_length = scene_length * SongFacade.signature_numerator()
        assert float(split_bar_length).is_integer()
        if bar_length < 2:
            raise Protocol0Warning("Scene should be at least 2 bars for splitting")
        if bar_length % 2 != 0:
            raise Protocol0Warning("Can only split scene with even bar length")
