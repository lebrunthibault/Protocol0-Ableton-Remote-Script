from functools import partial

from typing import TYPE_CHECKING

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.System import System
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class SessionToArrangementService(object):
    def __init__(self, song):
        # type: (Song) -> None
        self._song = song
        self._tempo = self._song.tempo
        self._is_bouncing = False
        DomainEventBus.subscribe(SongStoppedEvent, self._song_stopped_event_listener)

    def bounce_session_to_arrangement(self):
        # type: () -> None
        if self._is_bouncing:
            self._song.stop_playing()
            return None

        self._stop_playing_on_last_scene_end()
        self._bounce()

    def _bounce(self):
        # type: () -> None
        Scene.LOOPING_SCENE = None
        self._is_bouncing = True
        self._song.unfocus_all_tracks()
        self._tempo = self._song.tempo
        self._song.tempo = 999
        ApplicationView.show_arrangement()

        seq = Sequence()
        seq.add(System.client().clear_arrangement)
        seq.add(wait=20)
        seq.add(ApplicationView.show_session)
        seq.add(self._song.reset)

        # make recording start at 1.1.1
        seq.add(SongFacade.scenes()[0].pre_fire)
        seq.add(partial(setattr, self._song, "record_mode", True))
        seq.done()

    def _stop_playing_on_last_scene_end(self):
        # type: () -> None
        """ Stop the song when the last scene finishes """
        last_scene = SongFacade.scenes()[-1]
        seq = Sequence()
        seq.add(complete_on=last_scene.is_triggered_listener, no_timeout=True)
        seq.add(wait_for_event=BarChangedEvent)
        seq.add(self._song.stop_playing)
        seq.done()

    def _song_stopped_event_listener(self, _):
        # type: (SongStoppedEvent) -> None
        if not self._is_bouncing:
            return None

        self._song.reset()
        self._song.record_mode = False
        self._song.tempo = self._tempo
        self._song.back_to_arranger = False
        ApplicationView.show_arrangement()
        self._is_bouncing = False
