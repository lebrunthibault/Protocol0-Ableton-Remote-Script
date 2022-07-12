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
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.decorators import throttle
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.shared.SongFacade import SongFacade
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

    @property
    def _tracks_to_stop(self):
        # type: () -> Iterator[SimpleTrack]
        # manually stopping previous scene because we don't display clip slot stop buttons
        for track in self.clips.tracks:
            if track.is_playing:
                if (
                    self == SongFacade.playing_scene()
                    or track not in SongFacade.playing_scene().clips.tracks
                ):
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

        previous_playing_scene = SongFacade.playing_scene()
        Scene.PLAYING_SCENE = self
        if previous_playing_scene and previous_playing_scene != self:
            Scheduler.defer(partial(previous_playing_scene.stop, immediate=True))

    @property
    def next_scene(self):
        # type: () -> Scene
        if (
            self == SongFacade.looping_scene()
            or self == SongFacade.scenes()[-1]
            or SongFacade.scenes()[self.index + 1].bar_length == 0
        ):
            return self
        else:
            next_scene = SongFacade.scenes()[self.index + 1]
            if next_scene.skipped:
                return next_scene.next_scene
            else:
                return next_scene

    @property
    def previous_scene(self):
        # type: () -> Scene
        if self == SongFacade.scenes()[0]:
            return self
        else:
            previous_scene = SongFacade.scenes()[self.index - 1]
            if previous_scene.skipped:
                return previous_scene.previous_scene
            else:
                return previous_scene

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
        return SongFacade.is_playing() and any(
            clip and clip.is_playing and not clip.muted for clip in self.clips
        )

    @property
    def skipped(self):
        # type: () -> bool
        return self.name.strip().lower().startswith("skip")

    def on_last_beat(self):
        # type: () -> None
        if SongFacade.is_track_recording():
            return

        if self.playing_state.in_last_bar:
            next_scene = self.next_scene

            if next_scene != self:
                next_scene.fire()  # do not fire same scene as it focus it again (can lose current parameter focus)

    def fire(self):
        # type: () -> None
        # handles click sound when the previous scene plays shortly
        playing_scene = SongFacade.playing_scene()
        Scene.PLAYING_SCENE = self
        if playing_scene and playing_scene != self:
            playing_scene.stop()

        self._scene.fire()

        # ending scene
        if len(self.clips.un_muted_clips) == 0:
            Scheduler.wait_bars(self.bar_length, self.stop)

    def stop(self, immediate=False):
        # type: (bool) -> None
        """Used to manually stopping previous scene
        because we don't display clip slot stop buttons
        """
        DomainEventBus.emit(PlayingSceneChangedEvent())

        for track in self._tracks_to_stop:
            track.stop(immediate=immediate)

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
        seq.add(self.scene_name.update)
        seq.done()

    def mute_audio_tails(self):
        # type: () -> None
        for clip in self.clips.audio_tail_clips:
            clip.muted = True

    @throttle(duration=60)
    def fire_to_position(self, bar_length):
        # type: (int) -> Sequence
        self.scene_name.update(bar_position=bar_length)
        seq = Sequence()
        seq.add(self.fire)
        seq.defer()
        seq.add(partial(self.position_scroller.set_value, bar_length))

        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (bool) -> None
        next_track = ValueScroller.scroll_values(
            self.abstract_tracks, SongFacade.current_track(), go_next
        )
        next_track.select()
        next_clip_slot = next_track.selected_clip_slot
        if next_clip_slot.clip:
            next_track.select_clip_slot(next_clip_slot._clip_slot)

    def disconnect(self):
        # type: () -> None
        super(Scene, self).disconnect()
        self.scene_name.disconnect()
