from typing import TYPE_CHECKING, Tuple

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.shared.Colorer import Colorer
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger

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
        # it is not possible to crop an audio clip
        # so instead we notify clips that should be cropped by color and focus the last of them
        # usually only one audio clip will be long enough that it needs to be cropped
        audio_clip_to_crop = None

        for clip in scene.clips:
            if clip.length <= self._length:
                continue

            Logger.log_dev("%s : %s <-> %s" % (clip, clip.loop_start, clip.loop_end))
            clip.loop.end = clip.loop_start + self._end_length
            Logger.log_dev("new loop end %s" % (clip.loop_start + self._end_length))
            clip.loop.start += self._start_length
            Logger.log_dev("new loop start %s" % (clip.loop_start + self._start_length))

            if isinstance(clip, MidiClip):
                clip.crop()
            else:
                if clip.loop.start != 0:
                    audio_clip_to_crop = clip
                    Colorer.twinkle(clip, clip.color, ClipColorEnum.SHOULD_BE_CROPPED.color_int_value)

        if not self._contains_scene_end:
            for clip in scene.audio_tail_clips:
                clip.delete()

        if audio_clip_to_crop:
            Scheduler.defer(audio_clip_to_crop.select)

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
