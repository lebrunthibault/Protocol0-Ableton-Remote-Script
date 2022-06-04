from functools import partial

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ResetSongCommand import ResetSongCommand
from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SessionToArrangementService(object):
    def __init__(self,
                 playback_component,  # type: PlaybackComponent
                 recording_component,  # type: RecordingComponent
                 scene_component,  # type: SceneComponent
                 tempo_component,  # type: TempoComponent
                 track_component  # type: TrackComponent
                 ):
        # type: (...) -> None
        self._playback_component = playback_component
        self._recording_component = recording_component
        self._scene_component = scene_component
        self._tempo_component = tempo_component
        self._track_component = track_component

        self._tempo = self._tempo_component.tempo
        self._is_bouncing = False
        DomainEventBus.subscribe(SongStoppedEvent, self._song_stopped_event_listener)

    def bounce_session_to_arrangement(self):
        # type: () -> None
        if self._is_bouncing:
            self._playback_component.stop_playing()
            return None

        self._stop_playing_on_last_scene_end()
        self._bounce()

    def _bounce(self):
        # type: () -> None
        self._setup_bounce()

        seq = Sequence()
        seq.add(Backend.client().clear_arrangement)
        seq.wait(20)
        seq.add(ApplicationViewFacade.show_session)
        seq.add(partial(CommandBus.dispatch, ResetSongCommand()))

        # make recording start at 1.1.1
        seq.add(self._pre_fire_first_scene)
        seq.add(partial(setattr, self._recording_component, "record_mode", True))
        seq.done()

    def _setup_bounce(self):
        # type: () -> None
        self._scene_component.looping_scene_toggler.reset()
        self._is_bouncing = True
        self._track_component.unfocus_all_tracks(including_current=True)
        self._tempo = self._tempo_component.tempo
        self._tempo_component.tempo = 999
        ApplicationViewFacade.show_arrangement()

        for track in SongFacade.external_synth_tracks():
            if track.external_device.is_enabled:
                Backend.client().show_warning("Disabling external device of %s (for audio "
                                              "export)" % track)
                track.external_device.is_enabled = False

    def _pre_fire_first_scene(self):
        # type: () -> Sequence
        scene = SongFacade.scenes()[0]
        scene.fire()
        self._playback_component.stop_playing()
        seq = Sequence()
        seq.wait(2)
        return seq.done()

    def _stop_playing_on_last_scene_end(self):
        # type: () -> None
        """ Stop the song when the last scene finishes """
        self._scene_component.looping_scene_toggler.reset()
        seq = Sequence()
        seq.wait_for_event(SceneLastBarPassedEvent, SongFacade.last_scene()._scene)
        seq.add(SongFacade.last_scene().stop)
        seq.wait_bars(2)  # leaving some space for tails
        seq.add(self._playback_component.stop_playing)
        seq.done()

    def _song_stopped_event_listener(self, _):
        # type: (SongStoppedEvent) -> None
        if not self._is_bouncing:
            return None

        CommandBus.dispatch(ResetSongCommand())
        self._recording_component.record_mode = False
        self._tempo_component.tempo = self._tempo
        self._recording_component.back_to_arranger = False
        ApplicationViewFacade.show_arrangement()
        self._is_bouncing = False
