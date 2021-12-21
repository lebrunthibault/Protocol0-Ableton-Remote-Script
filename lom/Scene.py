from functools import partial

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
from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.utils.decorators import p0_subject_slot, throttle


class Scene(SceneActionMixin, AbstractObject):
    __subject_events__ = ("play",)

    PLAYING_SCENE = None  # type: Optional[Scene]
    LOOPING_SCENE = None  # type: Optional[Scene]
    SELECTED_DUPLICATE_SCENE_BAR_LENGTH = 4

    def __init__(self, scene, index, *a, **k):
        # type: (Live.Scene.Scene, int, Any, Any) -> None
        super(Scene, self).__init__(*a, **k)
        self._scene = scene
        self.index = index

        self.selected_playing_position = 0
        self.scene_name = SceneName(self)
        self._next_scene_fired = False

        self.clip_slots = []  # type: List[ClipSlot]
        self.clips = []  # type: List[Clip]
        self.tracks = []  # type: List[SimpleTrack]
        self._link_clip_slots_and_clips()

        # listeners
        self._is_triggered_listener.subject = self._scene
        self._play_listener.subject = self

    @property
    def live_id(self):
        # type: () -> int
        return self._scene._live_ptr

    def on_tracks_change(self):
        # type: () -> None
        self._link_clip_slots_and_clips()

    def _link_clip_slots_and_clips(self):
        # type: () -> None
        self.clip_slots = [track.clip_slots[self.index] for track in self.song.simple_tracks]
        self._map_clips()
        self.tracks = [cs.track for cs in self.clips]

        # listeners
        self._clip_slots_has_clip_listener.replace_subjects(self.clip_slots)

    def _map_clips(self):
        # type: () -> None
        self.clips = [clip_slot.clip for clip_slot in self.clip_slots if
                      clip_slot.has_clip and clip_slot.clip and clip_slot.track.__class__ not in (SimpleDummyTrack, SimpleInstrumentBusTrack)]
        self.audio_tail_clips = cast(List[AudioClip],
                                     [clip for clip in self.clips if isinstance(clip.track, SimpleAudioTailTrack)])
        self._clips_length_listener.replace_subjects(self.clips)

    def refresh_appearance(self):
        # type: (Scene) -> None
        self.scene_name.update()

    @p0_subject_slot("is_triggered")
    @throttle(wait_time=1)
    def _is_triggered_listener(self):
        # type: () -> None
        if self.song.is_playing is False:
            Scene.PLAYING_SCENE = None
            return

        if self.has_playing_clips:
            if self.song.playing_scene == self:
                self.parent.log_dev("notify end ! %s <-> %s" % (self.song.playing_scene, self))
                # noinspection PyUnresolvedReferences
                self.song.notify_session_end()
            else:
                if self.song.playing_scene:
                    self.song.playing_scene._next_scene_fired = False
                # noinspection PyUnresolvedReferences
                self.notify_play()

    @p0_subject_slot("play")
    def _play_listener(self):
        # type: () -> None
        self.parent.defer(partial(self._stop_previous_scene, self.song.playing_scene, immediate=True))
        self.parent.log_dev("setting to %s" % self)
        Scene.PLAYING_SCENE = self

        if self.song.looping_scene and self.song.looping_scene != self:
            previous_looping_scene = self.song.looping_scene
            Scene.LOOPING_SCENE = None
            self.parent.defer(previous_looping_scene.scene_name.update)

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

    @property
    def next_scene(self):
        # type: () -> Scene
        if self == self.song.looping_scene or self == self.song.scenes[-1] or self.song.scenes[self.index + 1].bar_length == 0:
            return self
        else:
            return self.song.scenes[self.index + 1]

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
        return int(self.playing_position / self.song.signature_numerator)

    @property
    def selected_bar(self):
        # type: () -> int
        if self.length == 0:
            return 0
        return int(self.selected_playing_position / self.song.signature_numerator)

    @property
    def has_playing_clips(self):
        # type: () -> bool
        return self.song.is_playing and any(clip.is_playing for clip in self.clips if clip)

    @property
    def longest_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self.clips if not clip.is_recording]
        return None if not len(clips) else max(clips, key=lambda c: c.length if c else 0)
