import Live
from typing import List, Any, Optional

from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.SceneActionMixin import SceneActionMixin
from a_protocol_0.lom.SceneName import SceneName
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.utils.decorators import p0_subject_slot, defer


class Scene(AbstractObject, SceneActionMixin):
    __subject_events__ = ("play",)

    PLAYING_SCENE = None  # type: Optional[Scene]
    LOOPING_SCENE = None  # type: Optional[Scene]

    def __init__(self, scene, *a, **k):
        # type: (Live.Scene.Scene, Any, Any) -> None
        super(Scene, self).__init__(*a, **k)
        self._scene = scene
        self.scene_name = SceneName(self)
        self.clip_slots = [
            self.song.clip_slots_by_live_live_clip_slot[clip_slot] for clip_slot in self._scene.clip_slots
        ]  # type: List[ClipSlot]

        # listeners
        self._is_triggered_listener.subject = self._scene
        self._play_listener.subject = self
        self._clip_slots_has_clip_listener.replace_subjects(self.clip_slots)
        self._clips_length_listener.replace_subjects(self.clips)

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        # type: () -> None
        if self.any_clip_playing:
            # noinspection PyUnresolvedReferences
            self.notify_play()

    @p0_subject_slot("play")
    @defer
    def _play_listener(self):
        # type: () -> None
        """ implements a next scene follow action """
        # doing this when scene starts playing
        Scene.PLAYING_SCENE = self
        if Scene.LOOPING_SCENE and Scene.LOOPING_SCENE != self:
            previous_looping_scene = Scene.LOOPING_SCENE
            Scene.LOOPING_SCENE = None
            previous_looping_scene.scene_name.update()
        self.schedule_next_scene_launch()

    @subject_slot_group("length")
    def _clips_length_listener(self, clip):
        # type: (Clip) -> None
        self._check_scene_length()

    @subject_slot_group("has_clip")
    def _clip_slots_has_clip_listener(self, clip_slot):
        # type: (ClipSlot) -> None
        self._clips_length_listener.replace_subjects(self.clips)
        self._check_scene_length()

    @property
    def index(self):
        # type: () -> int
        return self.song.scenes.index(self)

    @property
    def base_name(self):
        # type: () -> str
        return self.scene_name.base_name

    @property
    def color(self):
        # type: () -> int
        return self._scene.color

    @color.setter
    def color(self, color):
        # type: (int) -> None
        self._scene.color = color

    @property
    def is_triggered(self):
        # type: () -> bool
        return bool(self._scene.is_triggered)

    @property
    def name(self):
        # type: () -> str
        return self._scene.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._scene and name:
            self._scene.name = str(name).strip()

    @property
    def length(self):
        # type: () -> float
        return self.longest_clip.length if self.longest_clip else 0

    @property
    def bar_length(self):
        # type: () -> int
        return int(self.length / self.song.signature_denominator)

    @property
    def playing_position(self):
        # type: () -> float
        return self.longest_clip.playing_position if self.longest_clip else 0

    @property
    def looping(self):
        # type: () -> bool
        return self == Scene.LOOPING_SCENE

    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        Scene.LOOPING_SCENE = self if looping else None

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip_slot.clip for clip_slot in self.clip_slots if clip_slot.has_clip]

    @property
    def any_clip_playing(self):
        # type: () -> bool
        return any(clip.is_playing for clip in self.clips)

    @property
    def longest_clip(self):
        # type: () -> Optional[Clip]
        return None if not len(self.clips) else max(self.clips, key=lambda c: c.length)
