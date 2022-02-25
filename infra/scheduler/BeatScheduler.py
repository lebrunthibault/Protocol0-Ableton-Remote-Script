from _Framework.SubjectSlot import subject_slot
from typing import Callable, List

import Live
from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.scheduler.BeatSchedulerInterface import BeatSchedulerInterface
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.infra.scheduler.BeatSchedulerEvent import BeatSchedulerEvent
from protocol0.infra.scheduler.BeatTime import BeatTime
from protocol0.shared.SongFacade import SongFacade


class BeatScheduler(UseFrameworkEvents, BeatSchedulerInterface):
    """ BeatScheduler schedules action lists to be triggered after a specified
    number of bars. """

    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        super(BeatScheduler, self).__init__()
        self._song = song
        # noinspection PyArgumentList
        self._last_beats_song_time = BeatTime.from_song_beat_time(song.get_current_beats_song_time())
        self._scheduled_events = []  # type: List[BeatSchedulerEvent]
        self._is_playing_listener.subject = song

    @subject_slot('is_playing')
    def _is_playing_listener(self):
        # type: () -> None
        if not self._song.is_playing:
            self.restart()

    def _on_tick(self):
        # type: () -> None
        self._dispatch_timing_events()

        for event in self._scheduled_events:
            if event.should_execute:
                event.execute()
                self._scheduled_events.remove(event)

    def _dispatch_timing_events(self):
        # type: () -> None
        current_beats_song_time = BeatTime.from_song_beat_time(SongFacade.current_beats_song_time())

        events = []
        if current_beats_song_time.bars != self._last_beats_song_time.bars:
            events.append(BarChangedEvent())
            if SongFacade.playing_scene() and SongFacade.playing_scene().current_bar == SongFacade.playing_scene().bar_length - 1:
                events.append(SceneLastBarPassedEvent())

        if current_beats_song_time.in_last_beat and not self._last_beats_song_time.in_last_beat:
            events.append(LastBeatPassedEvent())

        if current_beats_song_time.in_last_32th and not self._last_beats_song_time.in_last_32th:
            events.append(Last32thPassedEvent())

        if current_beats_song_time.in_bar_ending and not self._last_beats_song_time.in_bar_ending:
            events.append(BarEndingEvent())

        self._last_beats_song_time = current_beats_song_time

        # NB: launching events in the loop can cause side effets
        # when _on_tick is called synchronously by live
        # and the loop might not be finished

        for event in events:
            DomainEventBus.notify(event)

    def wait_beats(self, beats_offset, callback):
        # type: (float, Callable) -> None
        """
        NB : the system internally relies on the Live timer's tick (every 17ms)
        So we cannot have precise execution
        Tip: never rely on wait_beats but use it in conjonction with listeners and Live quantization on launch
        It's the only way to have precise scheduling
        """
        # beats_offset -= 0.2  ?
        event = BeatSchedulerEvent(callback, BeatTime.make_from_beat_offset(beats_offset))
        self._scheduled_events.append(event)

    def restart(self):
        # type: () -> None
        self._scheduled_events[:] = []
