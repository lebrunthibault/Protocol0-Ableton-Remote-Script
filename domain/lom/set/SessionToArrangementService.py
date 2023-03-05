from functools import partial

import Live

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ResetPlaybackCommand import ResetPlaybackCommand
from protocol0.domain.audit.SetFixerService import SetFixerService
from protocol0.domain.audit.stats.SceneStats import SceneStats
from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.QuantizationComponent import QuantizationComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SessionToArrangementService(object):
    def __init__(
        self,
        playback_component,  # type: PlaybackComponent
        recording_component,  # type: RecordingComponent
        quantization_component,  # type: QuantizationComponent
        scene_component,  # type: SceneComponent
        tempo_component,  # type: TempoComponent
        track_component,  # type: TrackComponent
        set_fixer_service,  # type: SetFixerService
    ):
        # type: (...) -> None
        self._playback_component = playback_component
        self._recording_component = recording_component
        self._quantization_component = quantization_component
        self._scene_component = scene_component
        self._tempo_component = tempo_component
        self._track_component = track_component
        self._set_fixer_service = set_fixer_service

        self._tempo = self._tempo_component.tempo
        self.is_bouncing = False
        DomainEventBus.subscribe(SongStoppedEvent, self._song_stopped_event_listener)

        self._recorded_bar_length = 0
        DomainEventBus.subscribe(BarChangedEvent, self._on_bar_changed_event)

    def _on_bar_changed_event(self, _):
        # type: (BarChangedEvent) -> None
        self._recorded_bar_length += 1

    def bounce_session_to_arrangement(self):
        # type: () -> None
        if self.is_bouncing:
            self._playback_component.stop_playing()
            return None

        if not self._set_fixer_service.fix_set():
            return None

        self._stop_playing_on_last_scene_end()
        self._bounce()

    def _bounce(self):
        # type: () -> None
        self._setup_bounce()

        seq = Sequence()
        seq.add(ApplicationView.show_arrangement)
        seq.add(Backend.client().clear_arrangement)
        seq.wait_ms(700)
        seq.add(ApplicationView.show_session)
        seq.add(partial(CommandBus.dispatch, ResetPlaybackCommand()))
        self._quantization_component.clip_trigger_quantization = Live.Song.Quantization.q_half

        # make recording start at 1.1.1
        # seq.add(self._pre_fire_first_scene)
        seq.add(partial(setattr, self._recording_component, "record_mode", True))
        seq.defer()
        seq.wait_beats(1)
        seq.add(Song.scenes()[0].fire)
        seq.done()

    def _setup_bounce(self):
        # type: () -> None
        self._scene_component.looping_scene_toggler.reset()
        self.is_bouncing = True
        self._track_component.un_focus_all_tracks(including_current=True)
        self._reset_automation()
        self._tempo = self._tempo_component.tempo
        self._tempo_component.tempo = 750
        self._recorded_bar_length = 0

        for track in Song.external_synth_tracks():
            ext_device = find_if(
                lambda d: d.enum.is_external_device, list(track.midi_track.devices)
            )
            if ext_device.is_enabled:
                Backend.client().show_warning(
                    "Disabling external device of %s (for audio export)" % track
                )
                ext_device.is_enabled = False

    def _reset_automation(self):
        # type: () -> None
        """
        In the (rare) case automated parameters are not at their default
        we set them back
        Glitch can happen if an parameter automated in a following clip but not in the first
        has its value changed.
        The script does not fix up this case
        but does when the parameter is automated in the next clip
        """
        for track in Song.abstract_group_tracks():
            track.dummy_group.reset_all_automation()
    #
    # def _pre_fire_first_scene(self):
    #     # type: () -> Sequence
    #     scene = Song.scenes()[0]
    #     scene.fire()
    #     self._playback_component.stop_playing()
    #     seq = Sequence()
    #     seq.wait(2)
    #     return seq.done()

    def _stop_playing_on_last_scene_end(self):
        # type: () -> None
        """Stop the song when the last scene finishes"""
        self._scene_component.looping_scene_toggler.reset()

        seq = Sequence()
        seq.wait_for_event(SceneLastBarPassedEvent, Song.last_scene()._scene)
        seq.add(Song.last_scene().stop)
        if Song.last_scene().bar_length > 1:
            seq.wait_for_event(BarChangedEvent)

        seq.add(self._validate_recording_duration)
        seq.wait_bars(4)  # leaving some space for tails
        seq.add(self._playback_component.stop_playing)
        seq.done()

    def _song_stopped_event_listener(self, _):
        # type: (SongStoppedEvent) -> None
        if not self.is_bouncing:
            return None

        self._quantization_component.clip_trigger_quantization = Live.Song.Quantization.q_bar

        CommandBus.dispatch(ResetPlaybackCommand())
        self._recording_component.record_mode = False
        self._tempo_component.tempo = self._tempo
        self._recording_component.back_to_arranger = False
        ApplicationView.show_arrangement()
        self._playback_component.re_enable_automation()
        self.is_bouncing = False

    def _validate_recording_duration(self):
        # type: () -> None
        expected_bar_length = SceneStats().bar_length + 1  # empty 1st bar

        if expected_bar_length != self._recorded_bar_length:
            Backend.client().show_error(
                "Recording error, expected %s bars, got %s"
                % (expected_bar_length, self._recorded_bar_length)
            )
        else:
            Logger.info("Recording valid")
