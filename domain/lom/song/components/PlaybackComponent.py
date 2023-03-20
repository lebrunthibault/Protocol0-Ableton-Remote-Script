import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.event.RecordCancelledEvent import (
    RecordCancelledEvent,
)
from protocol0.domain.track_recorder.event.RecordEndedEvent import RecordEndedEvent
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class PlaybackComponent(SlotManager):
    _DEBUG = False

    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        super(PlaybackComponent, self).__init__()
        self._live_song = song
        self._is_playing = (
            False  # caching this because _is_playing_listener activates multiple times
        )
        self._is_playing_listener.subject = self._live_song
        DomainEventBus.subscribe(RecordEndedEvent, self._on_record_ended_event)
        DomainEventBus.subscribe(RecordCancelledEvent, self._on_record_cancelled_event)
        DomainEventBus.subscribe(ScenePositionScrolledEvent, self._on_scene_position_scrolled_event)
        DomainEventBus.subscribe(SongStoppedEvent, self._on_song_stopped_event)

    @subject_slot("is_playing")
    def _is_playing_listener(self):
        # type: () -> None
        # deduplicate calls with is_playing True
        if self.is_playing == self._is_playing:
            return
        else:
            self._is_playing = self.is_playing

        if not self.is_playing:
            DomainEventBus.defer_emit(SongStoppedEvent())
        else:
            if ApplicationView.is_session_visible():
                self.re_enable_automation()

            DomainEventBus.defer_emit(SongStartedEvent())

    def _on_scene_position_scrolled_event(self, _):
        # type: (ScenePositionScrolledEvent) -> None
        scene = Song.selected_scene()
        if scene.position_scroller.current_value == 0:
            beat_offset = 0.0
        else:
            beat_offset = (
                scene.position_scroller.current_value * Song.signature_numerator()
            ) - scene.playing_state.position
            # to catch the first beat transient
            beat_offset -= 0.5

        if self._DEBUG:
            Logger.info(
                "scene.position_scroller.current_value: %s" % scene.position_scroller.current_value
            )
            Logger.info("beat offset: %s" % beat_offset)

        self._live_song.scrub_by(beat_offset)

    def _on_record_ended_event(self, _):
        # type: (RecordEndedEvent) -> None
        self.metronome = False
        # this is delayed in the case an encoder is touched after the recording is finished by mistake
        for tick in [1, 10, 50, 100]:
            Scheduler.wait(tick, self.re_enable_automation)

    def _on_record_cancelled_event(self, _):
        # type: (RecordCancelledEvent) -> None
        self.metronome = False
        self._live_song.stop_playing()

    def _on_song_stopped_event(self, _):
        # type: (SongStoppedEvent) -> None
        self.metronome = False

    @property
    def is_playing(self):
        # type: () -> bool
        return self._live_song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        self._live_song.is_playing = is_playing

    def start_playing(self):
        # type: () -> None
        self._live_song.is_playing = True

    def stop(self):
        # type: () -> Sequence
        self.stop_all_clips(quantized=False)
        self.stop_playing()

        seq = Sequence()
        if Song.is_playing():
            seq.wait_for_event(SongStoppedEvent)
        return seq.done()

    def stop_playing(self):
        # type: () -> None
        self._live_song.stop_playing()

    def stop_all_clips(self, quantized=True):
        # type: (bool) -> None
        # noinspection PyTypeChecker
        self._live_song.stop_all_clips(quantized)

    def play_pause(self):
        # type: () -> None
        if self.is_playing:
            self.stop_playing()
        else:
            self.start_playing()

    def reset(self):
        # type: () -> None
        """stopping immediately"""
        self.stop_playing()
        # noinspection PyPropertyAccess
        self._live_song.current_song_time = 0
        self.stop_all_clips()

    @property
    def metronome(self):
        # type: () -> bool
        return self._live_song.metronome

    @metronome.setter
    def metronome(self, metronome):
        # type: (bool) -> None
        self._live_song.metronome = metronome

    def re_enable_automation(self):
        # type: () -> None
        self._live_song.re_enable_automation()
