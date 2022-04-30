import collections
from functools import partial

import Live
from typing import List, Optional, TYPE_CHECKING, Dict

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.scene.SceneActionMixin import SceneActionMixin
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneCropScroller import SceneCropScroller
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.lom.scene.ScenePlayingPosition import ScenePlayingPosition
from protocol0.domain.lom.scene.ScenePositionScroller import ScenePositionScroller
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable

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

        self.clips = SceneClips(self.index)
        self.clips.register_observer(self)
        self.scene_name = SceneName(self)
        self._scene_length = SceneLength(self.clips)
        self.playing_position = ScenePlayingPosition(self.clips, self._scene_length, self._song.scrub_by)
        self.crop_scroller = SceneCropScroller(self)
        self.position_scroller = ScenePositionScroller(self)

        # listeners
        self.is_triggered_listener.subject = self._scene

    def __repr__(self):
        # type: () -> str
        return "Scene %s (%s)" % (self.name, self.index)

    @property
    def live_id(self):
        # type: () -> int
        return self._scene._live_ptr

    @property
    def tracks(self):
        # type: () -> List[SimpleTrack]
        return [clip.track for clip in self.clips if not clip.muted]

    @property
    def abstract_tracks(self):
        # type: () -> List[AbstractTrack]
        tracks = collections.OrderedDict()  # type: Dict[int, AbstractTrack]
        for track in self.tracks:
            tracks[track.abstract_track.index] = track.abstract_track

        return tracks.values()

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, SceneClips):
            self.check_scene_length()

    def on_tracks_change(self):
        # type: () -> None
        self.clips.build()

    def on_added(self):
        # type: () -> None
        self.clips.on_added_scene()

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

    @property
    def next_scene(self):
        # type: () -> Scene
        if self == SongFacade.looping_scene() \
                or self == SongFacade.scenes()[-1] \
                or SongFacade.scenes()[self.index + 1].bar_length == 0:
            return self
        else:
            return SongFacade.scenes()[self.index + 1]

    @property
    def is_triggered(self):
        # type: () -> bool
        return bool(self._scene.is_triggered) if self._scene else False

    @property
    def name(self):
        # type: () -> str
        return self._scene and self._scene.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._scene and name:
            self._scene.name = str(name).strip()

    length = property(lambda self: self._scene_length.length)
    bar_length = property(lambda self: self._scene_length.bar_length)

    @property
    def has_playing_clips(self):
        # type: () -> bool
        return SongFacade.is_playing() and any(clip and clip.is_playing and not clip.muted for clip in self.clips)
