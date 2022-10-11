import collections
from functools import partial

import Live
from _Framework.SubjectSlot import SlotManager, subject_slot
from typing import List, Optional, Dict, cast

from protocol0.domain.lom.scene.NextSceneStartedEvent import NextSceneStartedEvent
from protocol0.domain.lom.scene.SceneAppearance import SceneAppearance
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneCropScroller import SceneCropScroller
from protocol0.domain.lom.scene.SceneFiredEvent import SceneFiredEvent
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.domain.lom.scene.ScenePositionScroller import ScenePositionScroller
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.timing import throttle
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class Scene(SlotManager):
    LAST_MANUALLY_STARTED_SCENE = None  # type: Optional[Scene]

    def __init__(self, live_scene, index):
        # type: (Live.Scene.Scene, int) -> None
        super(Scene, self).__init__()
        self._scene = live_scene
        self.index = index
        self.live_id = self._scene._live_ptr  # type: int

        self.clips = SceneClips(self.index)
        self._scene_length = SceneLength(self.clips, self.index)
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
            # add group tracks if they have automation on the scene
            for group_track in track.abstract_track.group_tracks:
                assert isinstance(group_track, AbstractGroupTrack)
                if group_track.dummy_group.has_automation(self.index):
                    tracks[group_track.index] = group_track

        return list(sorted(tracks.values(), key=lambda t: t.index))

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

    @property
    def next_scene(self):
        # type: () -> Scene
        if self.should_loop:
            return self
        else:
            next_scene = SongFacade.scenes()[self.index + 1]
            if next_scene.skipped:
                return next_scene.next_scene
            else:
                return next_scene

    @property
    def should_loop(self):
        # type: () -> bool
        return (
            self == SongFacade.looping_scene()
            or self == SongFacade.scenes()[-1]
            or SongFacade.scenes()[self.index + 1].bar_length == 0
        )

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
    def skipped(self):
        # type: () -> bool
        return self.name.strip().lower().startswith("skip")

    def on_end(self):
        # type: () -> None
        if SongFacade.is_track_recording() and not SongFacade.resampling_track().is_recording:
            return

        if self.playing_state.in_last_bar:
            next_scene = self.next_scene

            if next_scene != self:
                next_scene.fire()  # do not fire same scene as it focus it again (can lose current parameter focus)

                seq = Sequence()
                seq.wait_for_event(BarChangedEvent)
                seq.add(partial(DomainEventBus.emit, NextSceneStartedEvent(SongFacade.selected_scene().index)))
                seq.done()

    @subject_slot("is_triggered")
    def is_triggered_listener(self):
        # type: () -> None
        """
        This is called on scene trigger:
        - on click
        - and when the song stars playing

        We activate this only in the first case by checking PlayingSceneFacade
        This doesn't execute (duplicated) when the scene was fired from a command

        It is there to handle manual launches (direct click on scene)
        It could almost be removed as this case happens very rarely
        (I fire scenes almost always from keyboard shortcuts / commands)
        """
        if SongFacade.is_playing() is False or not self.playing_state.is_playing:
            return
        if SongFacade.playing_scene() == self:
            return

        DomainEventBus.emit(SceneFiredEvent(self.index))

    def fire(self):
        # type: () -> None
        """
        Fire the scene

        stop_tails == True will stop the tails immediately and is used
        when the scenes are not contiguous
        """
        # stop the previous scene in advance, using clip launch quantization
        DomainEventBus.emit(SceneFiredEvent(self.index))

        # only way to start all clips together
        if not SongFacade.is_playing():
            self._scene.fire()
        else:
            for track in SongFacade.abstract_tracks():
                track.fire(self.index)

    def stop(self, next_scene=None, immediate=False):
        # type: (Optional[Scene], bool) -> None
        """Used to manually stopping previous scene
        because we don't display clip slot stop buttons
        """
        for track in SongFacade.abstract_tracks():
            next_scene_index = next_scene.index if next_scene is not None else None
            track.stop(
                scene_index=self.index, immediate=immediate, next_scene_index=next_scene_index
            )

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
        seq.add(self.scene_name.update)
        seq.done()

    @throttle(duration=40)
    def fire_to_position(self, bar_length):
        # type: (int) -> Sequence
        seq = Sequence()

        if bar_length != 0:
            for track in SongFacade.abstract_tracks():
                if isinstance(track, ExternalSynthTrack):
                    track.prepare_for_scrub(self.index)
            seq.defer()  # for prepare_for_scrub to finish

        self.scene_name.update(bar_position=bar_length)
        seq.add(self.fire)
        seq.defer()
        seq.add(partial(self.position_scroller.set_value, bar_length))

        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (bool) -> None
        tracks = [track.get_view_track(self.index) for track in self.abstract_tracks]
        tracks = filter(None, tracks)
        tracks.sort(key=lambda t: t.index)
        next_track = ValueScroller.scroll_values(tracks, SongFacade.selected_track(), go_next)
        next_track.select()

        ApplicationViewFacade.focus_session()

    def unfold(self):
        # type: () -> None
        """Show only scene tracks"""
        for track in SongFacade.abstract_tracks():
            if track.is_foldable:
                track.is_folded = True

        for track in self.abstract_tracks:
            if track.is_foldable:
                track.is_folded = False
            if track.group_track:
                track.group_track.is_folded = False

    def disconnect(self):
        # type: () -> None
        super(Scene, self).disconnect()
        self.scene_name.disconnect()
