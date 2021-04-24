import Live
from typing import List, Any, Optional

from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.SceneName import SceneName
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.AudioBusTrack import AudioBusTrack
from a_protocol_0.utils.decorators import p0_subject_slot, defer


class Scene(AbstractObject):
    __subject_events__ = ("play",)

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
        self._clip_slots_map_clip_listener.replace_subjects(self.clip_slots)
        self._clips_length_listener.replace_subjects(self.clips)

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        # type: () -> None
        if self.any_clip_playing:
            # noinspection PyUnresolvedReferences
            self.notify_play()  # type: ignore

    @p0_subject_slot("play")
    def _play_listener(self):
        # type: () -> None
        """ implements a next scene follow action """
        # doing this when scene starts playing
        self.song.playing_scene = self
        self.schedule_next_scene_launch()

    @subject_slot_group("length")
    def _clips_length_listener(self, clip):
        # type: (Clip) -> None
        self.check_scene_length()

    @subject_slot_group("map_clip")
    def _clip_slots_map_clip_listener(self, clip_slot):
        # type: (ClipSlot) -> None
        self._clips_length_listener.replace_subjects(self.clips)
        self.check_scene_length()

    @defer
    def check_scene_length(self):
        # type: () -> None
        self.scene_name.update()
        self.schedule_next_scene_launch()

    def schedule_next_scene_launch(self):
        # type: () -> None
        self.parent.sceneBeatScheduler.clear()
        if self.index == len(self.song.scenes) - 1 or self.looping:
            return
        next_scene = self.song.scenes[self.index + 1]
        self.parent.sceneBeatScheduler.wait_beats(self.length - self.playing_position, next_scene.fire)

    def select(self):
        # type: () -> None
        self.song.selected_scene = self

    def fire(self):
        # type: () -> None
        if self._scene:
            self._scene.fire()

    def play_stop(self):
        # type: () -> None
        self.fire()

    def toggle_solo(self):
        # type: () -> None
        """ for a scene solo means looped """
        if not self.looping:  # solo activation
            previous_looping_scene = self.song.looping_scene
            self.song.looping_scene = self
            if self.song.playing_scene != self:
                self.fire()
            if previous_looping_scene:
                previous_looping_scene.scene_name.update()
            self.parent.sceneBeatScheduler.clear()  # clearing scene scheduling
        else:  # solo inactivation
            self.song.looping_scene = None
            self.schedule_next_scene_launch()  # restore previous behavior of follow action
        self.scene_name.update()

    @property
    def index(self):
        # type: () -> int
        return self.song.scenes.index(self)

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
        return self == self.song.looping_scene

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [
            clip_slot.clip
            for clip_slot in self.clip_slots
            if clip_slot.has_clip and not isinstance(clip_slot.track, AudioBusTrack)
        ]

    @property
    def any_clip_playing(self):
        # type: () -> bool
        return any(clip.is_playing for clip in self.clips)

    @property
    def longest_clip(self):
        # type: () -> Optional[Clip]
        return None if not len(self.clips) else max(self.clips, key=lambda c: c.length)
