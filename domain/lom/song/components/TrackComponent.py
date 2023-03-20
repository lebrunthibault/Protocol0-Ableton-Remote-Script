from functools import partial

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Iterator

from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.abstract_track.AbstractTrackSelectedEvent import (
    AbstractTrackSelectedEvent,
)
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song


class TrackComponent(SlotManager):
    def __init__(self, song_view):
        # type: (Live.Song.Song.View) -> None
        super(TrackComponent, self).__init__()
        self._song_view = song_view
        DomainEventBus.subscribe(
            SongInitializedEvent, lambda _: Scheduler.defer(partial(self.un_focus_all_tracks, True))
        )
        DomainEventBus.subscribe(AbstractTrackSelectedEvent, self._on_abstract_track_selected_event)
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._on_simple_track_armed_event)
        self._selected_track_listener.subject = self._song_view  # SongFacade is not hydrated

    @subject_slot("selected_track")
    def _selected_track_listener(self):
        # type: () -> None
        ApplicationView.focus_current_track()
        DomainEventBus.emit(SelectedTrackChangedEvent())

    def _on_abstract_track_selected_event(self, event):
        # type: (AbstractTrackSelectedEvent) -> None
        track = Song.live_track_to_simple_track(event.live_track)
        if track.group_track:
            track.group_track.is_folded = False
        if Song.selected_track() != track.base_track:
            self._song_view.selected_track = track._track

        scrollable_tracks = list(Song.scrollable_tracks())
        if len(scrollable_tracks) != 0 and track == scrollable_tracks[-1]:
            ApplicationView.focus_current_track()

    def _on_simple_track_armed_event(self, _):
        # type: (SimpleTrackArmedEvent) -> None
        if not Song.is_track_recording():
            self.un_focus_all_tracks()

    @property
    def abstract_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in Song.simple_tracks():
            if track.abstract_group_track:
                # skipping ExternalSynthTrack sub tracks
                if track.abstract_group_track.base_track == track:
                    yield track.abstract_group_track
            else:
                yield track

    @property
    def scrollable_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in self.abstract_tracks:
            if not track.is_visible:
                continue
            # when a group track is unfolded, will directly select the first sub_track
            if (
                isinstance(track, NormalGroupTrack)
                and not track.base_track.is_folded
                and isinstance(track.sub_tracks[0], SimpleTrack)
            ):
                continue
            yield track

    def un_focus_all_tracks(self, including_current=False):
        # type: (bool) -> None
        self._un_solo_all_tracks(including_current)
        self._un_arm_all_tracks(including_current)

    def _un_arm_all_tracks(self, including_current):
        # type: (bool) -> None
        for t in Song.armed_tracks():
            if not including_current and t.abstract_track == Song.current_track():
                continue
            t.arm_state.unarm()

    def _un_solo_all_tracks(self, including_current):
        # type: (bool) -> None
        for track in Song.abstract_tracks():
            if not including_current and track == Song.current_track():
                continue
            track.solo = False

    def scroll_tracks(self, go_next):
        # type: (bool) -> None
        if not Song.selected_track().IS_ACTIVE:
            next(Song.simple_tracks()).select()
            return None

        next_track = ValueScroller.scroll_values(
            Song.scrollable_tracks(), Song.current_track(), go_next, rotate=False
        )
        if next_track:
            next_track.select()
