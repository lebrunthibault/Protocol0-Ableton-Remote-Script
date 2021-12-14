from typing import List, Any, Optional, cast

import Live
from _Framework.SubjectSlot import subject_slot_group
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.SceneActionMixin import SceneActionMixin
from protocol0.lom.SceneName import SceneName
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip.Clip import Clip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
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
        self.clips = [clip_slot.clip for clip_slot in self.clip_slots if
                      clip_slot.has_clip and clip_slot.clip]
        self.audio_tail_clips = cast(List[AudioClip],
                                     [clip for clip in self.clips if isinstance(clip.track, SimpleAudioTailTrack)])
        self.tracks = [clip.track for clip in self.clips]
        self._clips_length_listener.replace_subjects(self.clips)

    def refresh_appearance(self):
        # type: (Scene) -> None
        self.scene_name.update()

    @p0_subject_slot("is_triggered")
    @throttle(wait_time=1)
    def _is_triggered_listener(self):
        # type: () -> None
        if self.has_playing_clips and Scene.PLAYING_SCENE != self:
            # noinspection PyUnresolvedReferences
            self.parent.defer(self.notify_play)
        if not self.has_playing_clips and Scene.PLAYING_SCENE != self.song.selected_scene:
            Scene.PLAYING_SCENE = None

    @p0_subject_slot("play")
    def _play_listener(self):
        # type: () -> None
        """ implements a next scene follow action """
        self._stop_previous_scene()
        Scene.PLAYING_SCENE = self

        if Scene.LOOPING_SCENE and Scene.LOOPING_SCENE != self:
            previous_looping_scene = Scene.LOOPING_SCENE
            Scene.LOOPING_SCENE = None
            previous_looping_scene.scene_name.update()

    @subject_slot_group("length")
    @throttle(wait_time=10)
    def _clips_length_listener(self, _):
        # type: (Clip) -> None
        self.check_scene_length()

    @subject_slot_group("has_clip")
    def _clip_slots_has_clip_listener(self, _):
        # type: (ClipSlot) -> None
        self._map_clips()
        self.check_scene_length()

    @subject_slot_group("stopped")
    def _clip_slots_stopped_listener(self, _):
        # type: (ClipSlot) -> None
        """ Stopping all clips cancels the next scene launch"""
        if not self.has_playing_clips:
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
        return bool(self._scene.is_triggered) if self._scene else False

    @property
    def is_recording(self):
        # type: () -> bool
        return any(clip for clip in self.clips if clip and clip.is_recording)

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
    def current_beat(self):
        # type: () -> int
        return int(self.playing_position % self.song.signature_numerator)

    @property
    def current_bar(self):
        # type: () -> int
        if self.length == 0:
            return 0
        current_beat = self.playing_position % self.length
        return int(current_beat) / self.song.signature_numerator

    @property
    def looping(self):
        # type: () -> bool
        return self == Scene.LOOPING_SCENE

    @property
    def has_playing_clips(self):
        # type: () -> bool
        return any(clip.is_playing for clip in self.clips if clip)

    @property
    def longest_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self.clips if not clip.is_recording]
        return None if not len(clips) else max(clips, key=lambda c: c.length if c else 0)
