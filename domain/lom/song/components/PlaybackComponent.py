import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.TrackRecordingCancelledEvent import (
    TrackRecordingCancelledEvent,
)
from protocol0.domain.track_recorder.TrackRecordingStartedEvent import TrackRecordingStartedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class PlaybackComponent(SlotManager):
    _DEBUG = True

    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        super(PlaybackComponent, self).__init__()
        self._live_song = song
        self._is_playing = (
            False  # caching this because _is_playing_listener activates multiple times
        )
        self.is_playing_listener.subject = self._live_song
        DomainEventBus.subscribe(TrackRecordingStartedEvent, lambda _: song.stop_playing())
        DomainEventBus.subscribe(TrackRecordingCancelledEvent, lambda _: song.stop_playing())
        DomainEventBus.subscribe(ScenePositionScrolledEvent, self._on_scene_position_scrolled_event)

    @subject_slot("is_playing")
    def is_playing_listener(self):
        # type: () -> None
        # deduplicate calls with is_playing True
        if self.is_playing == self._is_playing:
            return
        else:
            self._is_playing = self.is_playing

        if not self.is_playing:
            DomainEventBus.defer_emit(SongStoppedEvent())

            # iterating all scenes because we don't know which tail might be playing
            for scene in SongFacade.scenes():
                Scheduler.defer(scene.mute_audio_tails)
        else:
            DomainEventBus.defer_emit(SongStartedEvent())

    def _on_scene_position_scrolled_event(self, _):
        # type: (ScenePositionScrolledEvent) -> None
        scene = SongFacade.selected_scene()
        if scene.position_scroller.current_value == 0:
            beat_offset = 0.0
        else:
            beat_offset = (
                scene.position_scroller.current_value * SongFacade.signature_numerator()
            ) - scene.playing_state.position
            # to catch the first beat transient
            beat_offset -= 0.5

        if self._DEBUG:
            Logger.info(
                "scene.position_scroller.current_value: %s" % scene.position_scroller.current_value
            )
            Logger.info("beat offset: %s" % beat_offset)

        self._live_song.scrub_by(beat_offset)

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

    def stop_playing(self):
        # type: () -> None
        self._live_song.stop_playing()

    def stop_all_clips(self, quantized=True):
        # type: (bool) -> None
        # noinspection PyTypeChecker
        self._live_song.stop_all_clips(quantized)

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
