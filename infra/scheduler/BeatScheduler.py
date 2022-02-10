from typing import Callable, List

import Live
from _Framework.SubjectSlot import subject_slot
from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.scheduler.BeatChangedEvent import BeatChangedEvent
from protocol0.domain.shared.scheduler.BeatSchedulerInterface import BeatSchedulerInterface
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.infra.scheduler.BeatSchedulerEvent import BeatSchedulerEvent
from protocol0.infra.scheduler.BeatTime import BeatTime


class BeatScheduler(UseFrameworkEvents, BeatSchedulerInterface):
    """ BeatScheduler schedules action lists to be triggered after a specified
    number of bars. """

    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        super(BeatScheduler, self).__init__()
        self._song = song
        # noinspection PyArgumentList
        self._last_beats_song_time = BeatTime.make_from_beat_time(song.get_current_beats_song_time())
        self._scheduled_events = []  # type: List[BeatSchedulerEvent]
        self._is_playing_listener.subject = song
        self._current_song_time_listener.subject = song

    @subject_slot('is_playing')
    def _is_playing_listener(self):
        # type: () -> None
        if not self._song.is_playing:
            self.restart()

    @subject_slot('current_song_time')
    def _current_song_time_listener(self):
        # type: () -> None
        # noinspection PyArgumentList
        current_beats_song_time = BeatTime.make_from_beat_time(self._song.get_current_beats_song_time())

        if current_beats_song_time.beats != self._last_beats_song_time.beats:
            DomainEventBus.notify(BeatChangedEvent())

        if current_beats_song_time.in_last_32th and not self._last_beats_song_time.in_last_32th:
            DomainEventBus.notify(Last32thPassedEvent())

        if current_beats_song_time.in_bar_ending and not self._last_beats_song_time.in_bar_ending:
            DomainEventBus.notify(BarEndingEvent())

        for event in self._scheduled_events:
            if event.should_execute:
                event.execute()
                self._scheduled_events.remove(event)

        self._last_beats_song_time = current_beats_song_time

    def wait_beats(self, beat_count, callback):
        # type: (float, Callable) -> None
        # take into account the deferring of the event execution
        # at 120 BPM that's 0.025. A tick is 0.017 so that would mean the execution will happen 8ms
        # early. It's better than being late. NB : we could adapt this depending on the tempo
        # the system is not precise, often late, and we never want to have late executions
        beat_count -= 0.3
        event = BeatSchedulerEvent(callback, BeatTime.make_from_beat_count(beat_count))
        self._scheduled_events.append(event)

    def restart(self):
        # type: () -> None
        self._scheduled_events[:] = []
