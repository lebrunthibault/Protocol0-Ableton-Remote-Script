from functools import partial

from _Framework.SubjectSlot import subject_slot_group
from typing import List, Optional, cast, TYPE_CHECKING

import Live
from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.scene.SceneActionMixin import SceneActionMixin
from protocol0.domain.lom.scene.SceneCropScroller import SceneCropScroller
from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.lom.scene.ScenePositionScroller import ScenePositionScroller
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.decorators import p0_subject_slot, throttle
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class Scene(SceneActionMixin, UseFrameworkEvents):
    PLAYING_SCENE = None  # type: Optional[Scene]
    LAST_MANUALLY_STARTED_SCENE = None  # type: Optional[Scene]

    def __init__(self, scene, index, song):
        # type: (Live.Scene.Scene, int, Song) -> None
        super(Scene, self).__init__()
        self._scene = scene
        self.index = index
        self._song = song

        self.scene_name = SceneName(self)
        self.crop_scroller = SceneCropScroller(self)
        self.position_scroller = ScenePositionScroller(self)

        self.clip_slots = []  # type: List[ClipSlot]
        self.clips = []  # type: List[Clip]
        self.tracks = []  # type: List[SimpleTrack]
        self._link_clip_slots_and_clips()

        # listeners
        self.is_triggered_listener.subject = self._scene

    def __repr__(self):
        # type: () -> str
        return "Scene %s (%s)" % (self.name, self.index)

    @property
    def live_id(self):
        # type: () -> int
        return self._scene._live_ptr

    def on_tracks_change(self):
        # type: () -> None
        self._link_clip_slots_and_clips()

    def _link_clip_slots_and_clips(self):
        # type: () -> None
        self.clip_slots = [track.clip_slots[self.index] for track in SongFacade.simple_tracks()]
        self._map_clips()

        # listeners
        self._clip_slots_has_clip_listener.replace_subjects(self.clip_slots)

    def _map_clips(self):
        # type: () -> None
        clips = [clip_slot.clip for clip_slot in self.clip_slots if
                 clip_slot.has_clip and clip_slot.clip and clip_slot.track.__class__ not in (
                     SimpleDummyTrack, SimpleInstrumentBusTrack)]

        self.clips = [clip for clip in clips if not isinstance(clip, AudioTailClip)]
        self.audio_tail_clips = cast(List[AudioTailClip],
                                     [clip for clip in clips if isinstance(clip, AudioTailClip)])
        self._clips_length_listener.replace_subjects(self.clips)
        self._clips_muted_listener.replace_subjects([clip._clip for clip in self.clips])

        self.tracks = [clip.track for clip in self.clips if not clip.muted]

    def refresh_appearance(self):
        # type: (Scene) -> None
        self.scene_name.update()

    @p0_subject_slot("is_triggered")
    def is_triggered_listener(self):
        # type: () -> None
        if SongFacade.is_playing() is False or not self.has_playing_clips:
            return

        if SongFacade.playing_scene() and SongFacade.playing_scene() != self:
            Scheduler.defer(partial(self._stop_previous_scene, SongFacade.playing_scene(), immediate=True))
        Scene.PLAYING_SCENE = self

    @subject_slot_group("has_clip")
    def _clip_slots_has_clip_listener(self, _):
        # type: (ClipSlot) -> None
        self._map_clips()
        self.check_scene_length()

    @subject_slot_group("length")
    @throttle(wait_time=10)
    def _clips_length_listener(self, _):
        # type: (Clip) -> None
        self.check_scene_length()

    @subject_slot_group("muted")
    def _clips_muted_listener(self, _):
        # type: (Clip) -> None
        self._map_clips()
        self.check_scene_length()

    @property
    def next_scene(self):
        # type: () -> Scene
        if self == SongFacade.looping_scene() or self == SongFacade.scenes()[-1] or SongFacade.scenes()[self.index + 1].bar_length == 0:
            return self
        else:
            return SongFacade.scenes()[self.index + 1]

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
        if self.length % SongFacade.signature_numerator() != 0:
            Logger.log_warning("%s invalid length: %s, longest_clip track: %s" % (
                self, self.length, self.longest_clip.track.abstract_track))
        return int(self.length / SongFacade.signature_numerator())

    @property
    def playing_position(self):
        # type: () -> float
        if self.longest_un_muted_clip:
            return self.longest_un_muted_clip.playing_position - self.longest_un_muted_clip.start_marker
        else:
            return 0

    @property
    def playing_bar_position(self):
        # type: () -> float
        return self.playing_position / SongFacade.signature_numerator()

    @property
    def current_bar(self):
        # type: () -> int
        if self.length == 0:
            return 0
        return int(self.playing_bar_position)

    @property
    def has_playing_clips(self):
        # type: () -> bool
        return SongFacade.is_playing() and any(clip and clip.is_playing and not clip.muted for clip in self.clips)

    @property
    def longest_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self.clips if not clip.is_recording]
        if len(clips) == 0:
            return None
        else:
            return max(clips, key=lambda c: c.length)

    @property
    def longest_un_muted_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self.clips if not clip.is_recording and not clip.muted]
        if len(clips) == 0:
            return None
        else:
            return max(clips, key=lambda c: c.length)
