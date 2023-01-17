import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Callable, List

from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.scheduler.BeatSchedulerInterface import BeatSchedulerInterface
from protocol0.domain.shared.scheduler.Last16thPassedEvent import Last16thPassedEvent
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.shared.scheduler.Last8thPassedEvent import Last8thPassedEvent
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.ThirdBeatPassedEvent import ThirdBeatPassedEvent
from protocol0.infra.scheduler.BeatSchedulerEvent import BeatSchedulerEvent
from protocol0.infra.scheduler.BeatTime import BeatTime
from protocol0.shared.Song import Song


class BeatScheduler(SlotManager, BeatSchedulerInterface):
    """BeatScheduler schedules action lists to be triggered after a specified
    number of bars."""

    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        super(BeatScheduler, self).__init__()
        self._song = song
        # noinspection PyArgumentList
        self._last_beats_song_time = BeatTime.from_song_beat_time(
            song.get_current_beats_song_time()
        )
        self._scheduled_events = []  # type: List[BeatSchedulerEvent]
        self._is_playing_listener.subject = song

    @subject_slot("is_playing")
    def _is_playing_listener(self):
        # type: () -> None
        if not self._song.is_playing:
            self._execute_events()  # execute song stopped events
            self.reset()

    def _on_tick(self):
        # type: () -> None
        self._dispatch_timing_events()
        self._execute_events()

    def _execute_events(self):
        # type: () -> None
        for event in self._scheduled_events:
            if event.should_execute:
                event.execute()
                self._scheduled_events.remove(event)

    def _dispatch_timing_events(self):
        # type: () -> None
        current_beats_song_time = BeatTime.from_song_beat_time(Song.current_beats_song_time())

        events = []  # type: List[object]
        if (
            current_beats_song_time.bars != self._last_beats_song_time.bars
            and not self._last_beats_song_time.is_start
        ):
            events.append(BarChangedEvent())
            playing_scene = Song.playing_scene()
            if playing_scene is not None and playing_scene.playing_state.in_last_bar:
                events.append(SceneLastBarPassedEvent(playing_scene._scene))

        if current_beats_song_time.beats == 3 and not self._last_beats_song_time.beats == 3:
            events.append(ThirdBeatPassedEvent())

        if current_beats_song_time.in_last_beat and not self._last_beats_song_time.in_last_beat:
            events.append(LastBeatPassedEvent())

        if current_beats_song_time.in_last_8th and not self._last_beats_song_time.in_last_8th:
            events.append(Last8thPassedEvent())

        if current_beats_song_time.in_last_16th and not self._last_beats_song_time.in_last_16th:
            events.append(Last16thPassedEvent())

        if current_beats_song_time.in_last_32th and not self._last_beats_song_time.in_last_32th:
            events.append(Last32thPassedEvent())

        if current_beats_song_time.in_bar_ending and not self._last_beats_song_time.in_bar_ending:
            events.append(BarEndingEvent())

        self._last_beats_song_time = current_beats_song_time

        # NB: launching events in the loop can cause side effects
        # when _on_tick is called synchronously by live
        # and the loop might not be finished

        for event in events:
            DomainEventBus.emit(event)

    def wait_beats(self, beats_offset, callback, execute_on_song_stop):
        # type: (float, Callable, bool) -> None
        """
        NB : the system internally relies on the Live timer's tick (every 17ms)
        So we cannot have precise execution
        Tip: never rely on wait_beats but use it in conjunction with listeners and Live quantization on launch
        It's the only way to have precise scheduling
        """
        event = BeatSchedulerEvent(
            callback, BeatTime.make_from_beat_offset(beats_offset), execute_on_song_stop
        )
        if beats_offset == 0:
            event.execute()
        else:
            self._scheduled_events.append(event)

    def disconnect(self):
        # type: () -> None
        super(BeatScheduler, self).disconnect()
        self.reset()

    def reset(self):
        # type: () -> None
        self._scheduled_events[:] = []
        self._last_beats_song_time = BeatTime(1, 1, 1, 1)
