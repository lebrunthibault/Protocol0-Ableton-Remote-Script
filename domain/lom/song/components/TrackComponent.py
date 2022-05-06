import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Iterator

from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.abstract_track.AbstractTrackSelectedEvent import AbstractTrackSelectedEvent
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackComponent(SlotManager):
    def __init__(self, song_view):
        # type: (Live.Song.Song.View) -> None
        super(TrackComponent, self).__init__()
        self._song_view = song_view
        DomainEventBus.subscribe(SongInitializedEvent, lambda _: Scheduler.defer(self.unfocus_all_tracks))
        DomainEventBus.subscribe(AbstractTrackSelectedEvent, self._on_abstract_track_selected_event)
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._on_simple_track_armed_event)
        self._selected_track_listener.subject = self._song_view  # SongFacade is not hydrated

    @subject_slot("selected_track")
    def _selected_track_listener(self):
        # type: () -> None
        ApplicationViewFacade.focus_current_track()
        DomainEventBus.emit(SelectedTrackChangedEvent())

    def _on_abstract_track_selected_event(self, event):
        # type: (AbstractTrackSelectedEvent) -> None
        self.select_track(event.track)

    def _on_simple_track_armed_event(self, _):
        # type: (SimpleTrackArmedEvent) -> None
        self.unfocus_all_tracks()

    @property
    def abstract_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in SongFacade.simple_tracks():
            if isinstance(track, SimpleInstrumentBusTrack) or track == SongFacade.usamo_track():  # type: ignore[unreachable]
                continue
            if isinstance(track.abstract_track, NormalGroupTrack):  # type: ignore[unreachable]
                yield track  # yield all normal group track sub tracks
            elif track == track.abstract_track.base_track:
                yield track.abstract_track  # return the abstract track for external synth tracks

    @property
    def scrollable_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in self.abstract_tracks:
            if not track.is_visible:
                continue
            # when a group track is unfolded, will directly select the first sub_trackB
            if isinstance(track, NormalGroupTrack) and not track.is_folded and isinstance(track.sub_tracks[0],
                                                                                          SimpleTrack):
                continue
            yield track

    def select_track(self, abstract_track):
        # type: (AbstractTrack) -> Sequence
        if abstract_track.group_track:
            abstract_track.group_track.is_folded = False
        seq = Sequence()
        if SongFacade.selected_track() != abstract_track.base_track:
            self._song_view.selected_track = abstract_track._track
            seq.defer()
        return seq.done()

    def unfocus_all_tracks(self):
        # type: () -> None
        self._unsolo_all_tracks()
        self._unarm_all_tracks()

    def _unarm_all_tracks(self):
        # type: () -> None
        for t in SongFacade.partially_armed_tracks():
            if t.abstract_track != SongFacade.current_track():
                t.arm_state.unarm()

    def _unsolo_all_tracks(self):
        # type: () -> None
        for t in SongFacade.abstract_tracks():
            if t.solo and t != SongFacade.current_track():
                t.solo = False

    def scroll_tracks(self, go_next):
        # type: (bool) -> None
        if not SongFacade.selected_track().IS_ACTIVE:
            next(SongFacade.simple_tracks()).select()
            return None

        next_track = scroll_values(SongFacade.scrollable_tracks(), SongFacade.current_track(), go_next, rotate=False)
        if next_track:
            next_track.select()
