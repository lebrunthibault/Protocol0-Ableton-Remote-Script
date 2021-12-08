from typing import List, Any, Optional

import Live
from _Framework.SubjectSlot import subject_slot_group
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.SceneActionMixin import SceneActionMixin
from protocol0.lom.SceneName import SceneName
from protocol0.lom.clip.Clip import Clip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.utils.decorators import p0_subject_slot, throttle


class Scene(SceneActionMixin, AbstractObject):
    __subject_events__ = ("play",)

    PLAYING_SCENE = None  # type: Optional[Scene]
    LOOPING_SCENE = None  # type: Optional[Scene]
    SELECTED_DUPLICATE_SCENE_BAR_LENGTH = 4

    def __init__(self, scene, *a, **k):
        # type: (Live.Scene.Scene, Any, Any) -> None
        super(Scene, self).__init__(*a, **k)
        self._scene = scene
        self.clip_slots = []  # type: List[ClipSlot]
        self.clips = []  # type: List[Clip]
        self.tracks = []  # type: List[SimpleTrack]
        self.scene_name = SceneName(self)
        # listeners
        self._is_triggered_listener.subject = self._scene
        self._play_listener.subject = self

    def link_clip_slots_and_clips(self):
        # type: () -> None
        try:
            self.clip_slots = [
                self.song.live_clip_slot_to_clip_slot[clip_slot] for clip_slot in self._scene.clip_slots
            ]
        except KeyError:
            self.parent.songManager.tracks_listener(purge=True)
            return

        # listeners
        self._clip_slots_has_clip_listener.replace_subjects(self.clip_slots)
        self._clip_slots_stopped_listener.replace_subjects(self.clip_slots)
        self._clips_length_listener.replace_subjects(self.clips)
        self._map_clips()

    def _map_clips(self):
        # type: () -> None
        self.clips = [clip_slot.clip for clip_slot in self.clip_slots if clip_slot.has_clip and clip_slot.clip and not clip_slot.clip.muted]
        self.tracks = [clip.track for clip in self.clips]
        self._clips_length_listener.replace_subjects(self.clips)
        self._check_scene_length()

    def refresh_appearance(self):
        # type: (Scene) -> None
        self.scene_name.update()

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        # type: () -> None
        if self.is_playing:
            Scene.PLAYING_SCENE = self
            # noinspection PyUnresolvedReferences
            self.notify_play()
            return

        # Scene is triggered but not yet playing
        if Scene.PLAYING_SCENE and Scene.PLAYING_SCENE != self:
            # manually stopping previous scene because we don't display clip slot stop buttons
            for clip in Scene.PLAYING_SCENE.clips:
                if clip.track not in self.tracks:
                    clip.stop()

    @p0_subject_slot("play")
    def _play_listener(self):
        # type: () -> None
        """ implements a next scene follow action """
        if Scene.LOOPING_SCENE and Scene.LOOPING_SCENE != self:
            previous_looping_scene = Scene.LOOPING_SCENE
            Scene.LOOPING_SCENE = None
            self.parent.defer(previous_looping_scene.scene_name.update)
        self.schedule_next_scene_launch()

    @subject_slot_group("length")
    @throttle(wait_time=20)
    def _clips_length_listener(self, _):
        # type: (Clip) -> None
        self._check_scene_length()

    @subject_slot_group("has_clip")
    def _clip_slots_has_clip_listener(self, _):
        # type: (ClipSlot) -> None
        self._map_clips()
        self._check_scene_length()

    @subject_slot_group("stopped")
    def _clip_slots_stopped_listener(self, _):
        # type: (ClipSlot) -> None
        """ Stopping all clips cancels the next scene launch"""
        self.parent.sceneBeatScheduler.clear()

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
        return self._scene and self._scene.color

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        if self._scene:
            self._scene.color = color_index

    @property
    def is_triggered(self):
        # type: () -> bool
        if self._scene:
            return bool(self._scene.is_triggered)

    @property
    def name(self):
        # type: () -> str
        return self._scene and self._scene.name

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
        if self.length % self.song.signature_numerator != 0:
            self.parent.log_warning("%s invalid length: %s, longest_clip track: %s" % (
                self, self.length, self.longest_clip.track.abstract_track))
        return int(self.length / self.song.signature_numerator)

    @property
    def playing_position(self):
        # type: () -> float
        if self.longest_clip:
            return self.longest_clip.playing_position - self.longest_clip.start_marker
        else:
            return 0

    @property
    def looping(self):
        # type: () -> bool
        return self == Scene.LOOPING_SCENE

    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        Scene.LOOPING_SCENE = self if looping else None

    @property
    def is_playing(self):
        # type: () -> bool
        return any(clip.is_playing for clip in self.clips if clip)

    @property
    def longest_clip(self):
        # type: () -> Optional[Clip]
        return None if not len(self.clips) else max(self.clips, key=lambda c: c.length if c else 0)
