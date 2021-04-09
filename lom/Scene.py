import Live
from typing import List

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.SceneName import SceneName
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.AudioBusTrack import AudioBusTrack
from a_protocol_0.utils.decorators import p0_subject_slot


class Scene(AbstractObject):
    def __init__(self, scene, index, *a, **k):
        # type: (Live.Scene.Scene, int) -> None
        super(Scene, self).__init__(*a, **k)
        self.index = index
        self._scene = scene
        self.scene_name = SceneName(self)
        self._is_triggered_listener.subject = self._scene
        self.clip_slots = [self.song.clip_slots_by_live_live_clip_slot[clip_slot] for clip_slot in
                           self._scene.clip_slots]  # type: List[ClipSlot]

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        if not self.is_triggered and self.scene_name.bar_count and self.index < len(self.song.scenes) - 1:
            self.parent.wait_bars(self.scene_name.bar_count, self.song.scenes[self.index + 1].fire)

    def select(self):
        self.song.selected_scene = self

    def fire(self):
        if self._scene:
            self._scene.fire()

    def update_name(self, show_bar_count=False):
        """ toggle bar count and change base_name if index based """
        if self.scene_name.bar_count and not show_bar_count:
            self.scene_name.bar_count = None
        elif self.longest_clip:
            self.scene_name.bar_count = int(self.longest_clip.length) / self.song.signature_denominator

        self.scene_name.update()

    @staticmethod
    def update_all_names():
        from a_protocol_0 import Protocol0
        scenes = Protocol0.SELF.protocol0_song.scenes
        bar_count_states = set([bool(scene.scene_name.bar_count) for scene in scenes])
        if len(bar_count_states) > 1:
            [scene.update_name(show_bar_count=True) for scene in scenes]
        else:
            [scene.update_name() for scene in scenes]

    @property
    def color(self):
        # type: () -> int
        return self._scene.color

    @color.setter
    def color(self, color):
        self._scene.color = color

    @property
    def is_triggered(self):
        # type: () -> int
        return self._scene.is_triggered

    @property
    def name(self):
        # type: () -> int
        return self._scene.name

    @name.setter
    def name(self, name):
        if self._scene and name:
            self._scene.name = name

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip_slot.clip for clip_slot in self.clip_slots if clip_slot.has_clip and not isinstance(clip_slot.track, AudioBusTrack)]

    @property
    def longest_clip(self):
        # type: () -> Clip
        return None if not len(self.clips) else max(self.clips, key=lambda c: c.length)
