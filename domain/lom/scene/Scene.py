import collections
from collections import Iterator
from functools import partial

import Live
from _Framework.SubjectSlot import SlotManager, subject_slot
from typing import List, Optional, Dict, cast

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.scene.PlayingSceneChangedEvent import PlayingSceneChangedEvent
from protocol0.domain.lom.scene.PlayingSceneFacade import PlayingSceneFacade
from protocol0.domain.lom.scene.SceneAppearance import SceneAppearance
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneCropScroller import SceneCropScroller
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.domain.lom.scene.ScenePositionScroller import ScenePositionScroller
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
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

        return list(sorted(tracks.values(), key=lambda t: t.index))

    def _clips_to_stop(self, immediate):
        # type: (bool) -> Iterator[Clip]
        # manually stopping previous scene because we don't display clip slot stop buttons
        clips = self.clips.all if immediate else list(self.clips)
        for clip in clips:
            if not clip.is_playing:
                continue

            yield clip

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

    def on_last_beat(self):
        # type: () -> None
        if SongFacade.is_track_recording():
            return

        if self.playing_state.in_last_bar:
            next_scene = self.next_scene

            if next_scene != self:
                next_scene.fire()  # do not fire same scene as it focus it again (can lose current parameter focus)

    @subject_slot("is_triggered")
    def is_triggered_listener(self):
        # type: () -> None
        """
        This is called on scene trigger

        It is there to handle manual launches (direct click on scene)
        It could almost be removed as this case happens very rarely
        (I fire my scenes almost always from keyboard shortcuts --> from commands)
        """
        if SongFacade.is_playing() is False or not self.playing_state.is_playing:
            return

        # this will stop the previous scene in case of manual trigger
        # immediate False would play the clips at least one more bar
        # This doesn't execute (duplicated) when the scene was fired from a command
        if SongFacade.playing_scene() != self:
            Scheduler.defer(partial(self._stop_playing_scene, immediate=True))
            PlayingSceneFacade.set(self)

    def reset_automations(self, previous_playing_scene):
        # type: (Scene) -> None
        """Will reset automations not present in the scene tracks"""
        for track in previous_playing_scene.clips.tracks:
            if isinstance(track, SimpleDummyTrack):
                track.reset_automation(self.index, previous_playing_scene.index)

    def fire(self, stop_tails=False):
        # type: (bool) -> None
        """
        Fire the scene

        stop_tails == True will stop the tails immediately and is used
        when the scenes are not contiguous
        """
        # stop the previous scene in advance, using clip launch quantization
        self._stop_playing_scene(immediate=stop_tails)

        # only way to start all clips together
        if not SongFacade.is_playing():
            self._scene.fire()
        else:
            for track in self.abstract_tracks:
                track.fire(self.index)

        # update the playing scene singleton at the next bar
        seq = Sequence()
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
        seq.add(partial(PlayingSceneFacade.set, self))
        seq.done()

    def _stop_playing_scene(self, immediate=False):
        # type: (bool) -> None
        """Stop the previous scene : quantized or immediate"""
        if SongFacade.playing_scene() is not None and SongFacade.playing_scene() != self:
            SongFacade.playing_scene().stop(immediate)

    def stop(self, immediate=False):
        # type: (bool) -> None
        """Used to manually stopping previous scene
        because we don't display clip slot stop buttons
        """
        DomainEventBus.emit(PlayingSceneChangedEvent())

        for clip in self._clips_to_stop(immediate):
            clip.stop(immediate=immediate)

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
        seq.add(self.scene_name.update)
        seq.done()

    def mute_audio_tails(self):
        # type: () -> None
        for clip in self.clips.audio_tail_clips:
            clip.muted = True

    @throttle(duration=40)
    def fire_to_position(self, bar_length):
        # type: (int) -> Sequence
        seq = Sequence()

        if bar_length != 0:
            for track in self.abstract_tracks:
                if isinstance(track, ExternalSynthTrack):
                    track.prepare_for_scrub(self.index)
            seq.defer()  # for prepare_for_scrub to finish

        self.scene_name.update(bar_position=bar_length)
        seq.add(partial(self.fire, stop_tails=True))
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

        # selects the track owning the main clip slot (midi track for ext track)
        # next_clip_slot = next_track.selected_clip_slot
        # if next_clip_slot.clip:
        #     next_track.select_clip_slot(next_clip_slot._clip_slot)

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
