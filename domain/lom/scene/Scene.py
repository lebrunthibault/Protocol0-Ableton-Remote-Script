import collections
from collections import Iterator
from functools import partial

import Live
from _Framework.SubjectSlot import SlotManager, subject_slot
from typing import List, Optional, Dict, cast

from protocol0.domain.lom.scene.PlayingSceneChangedEvent import PlayingSceneChangedEvent
from protocol0.domain.lom.scene.SceneAppearance import SceneAppearance
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneCropScroller import SceneCropScroller
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.domain.lom.scene.ScenePositionScroller import ScenePositionScroller
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import scroll_values, ForwardTo
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class Scene(SlotManager):
    PLAYING_SCENE = None  # type: Optional[Scene]
    LAST_MANUALLY_STARTED_SCENE = None  # type: Optional[Scene]

    def __init__(self, live_scene, index):
        # type: (Live.Scene.Scene, int) -> None
        super(Scene, self).__init__()
        self._scene = live_scene
        self.index = index
        self.live_id = self._scene._live_ptr  # type: int

        self.clips = SceneClips(self.index)
        self._scene_length = SceneLength(self.clips)
        self.playing_state = ScenePlayingState(self.clips, self._scene_length)
        self.scene_name = SceneName(live_scene, self._scene_length, self.playing_state)
        self.appearance = SceneAppearance(live_scene, self.scene_name)
        self.crop_scroller = SceneCropScroller(self._scene_length)
        self.position_scroller = ScenePositionScroller(self._scene_length, self.playing_state)

        # listeners
        self.clips.register_observer(self)
        self.is_triggered_listener.subject = self._scene

    def __repr__(self):
        # type: () -> str
        return "Scene %s (%s)" % (self.name, self.index)

    @property
    def abstract_tracks(self):
        # type: () -> List[AbstractTrack]
        tracks = collections.OrderedDict()  # type: Dict[int, AbstractTrack]
        for track in self.clips.tracks:
            tracks[track.abstract_track.index] = track.abstract_track

        return tracks.values()

    def _tracks_to_stop(self, scene):
        # type: (Scene) -> Iterator[SimpleTrack]
        # manually stopping previous scene because we don't display clip slot stop buttons
        Logger.dev("scene.clips.tracks: %s" % list(scene.clips.tracks))
        for track in scene.clips.tracks:
            if track.is_playing and track not in self.clips.tracks:
                yield track

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, SceneClips):
            self.appearance.refresh()

    def on_tracks_change(self):
        # type: () -> None
        self.clips.build()

    def on_added(self):
        # type: () -> None
        self.clips.on_added_scene()
        self.scene_name.update("")

    @subject_slot("is_triggered")
    def is_triggered_listener(self):
        # type: () -> None
        if SongFacade.is_playing() is False or not self.playing_state.has_playing_clips:
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

    name = cast(str, ForwardTo("appearance", "name"))
    length = cast(float, ForwardTo("_scene_length", "length"))
    bar_length = cast(int, ForwardTo("_scene_length", "bar_length"))

    @property
    def has_playing_clips(self):
        # type: () -> bool
        return SongFacade.is_playing() and any(clip and clip.is_playing and not clip.muted for clip in self.clips)

    def on_last_beat(self):
        # type: (Scene) -> None
        if SongFacade.is_track_recording():
            return

        if self.playing_state.in_last_bar:
            next_scene = self.next_scene

            if next_scene != self:
                next_scene.fire()  # do not fire same scene as it focus it again (can lose current parameter focus)

    def fire(self):
        # type: (Scene) -> None
        # handles click sound when the previous scene plays shortly
        playing_scene = SongFacade.playing_scene()
        if playing_scene and playing_scene != self:
            self._stop_previous_scene(playing_scene)

        Scene.PLAYING_SCENE = self

        self._scene.fire()

    def _stop_previous_scene(self, previous_playing_scene, immediate=False):
        # type: (Scene, Scene, bool) -> None
        DomainEventBus.emit(PlayingSceneChangedEvent())

        # manually stopping previous scene because we don't display clip slot stop buttons
        Logger.dev("tracks to stop : %s" % list(self._tracks_to_stop(previous_playing_scene)))
        for track in self._tracks_to_stop(previous_playing_scene):
            track.stop(immediate=immediate)

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent)
        seq.add(previous_playing_scene.scene_name.update)
        seq.done()

    def mute_audio_tails(self):
        # type: (Scene) -> None
        for clip in self.clips.audio_tail_clips:
            clip.muted = True

    def fire_to_position(self, bar_length):
        # type: (Scene, int) -> Sequence
        self.scene_name.update(bar_position=bar_length)
        seq = Sequence()
        seq.add(self.fire)
        seq.defer()
        seq.add(partial(self.position_scroller.set_value, bar_length))

        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (Scene, bool) -> None
        next_track = scroll_values(self.abstract_tracks, SongFacade.current_track(), go_next)
        next_track.select()
        next_clip_slot = next_track.clip_slots[SongFacade.selected_scene().index]
        if next_clip_slot.clip:
            next_track.select_clip_slot(next_clip_slot._clip_slot)

    def disconnect(self):
        # type: () -> None
        super(Scene, self).disconnect()
        self.clips.disconnect()
        self.scene_name.disconnect()
