from functools import partial

from typing import Optional

import Live
from protocol0.domain.command.ResetSongCommand import ResetSongCommand
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.CommandBus import CommandBus
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.System import System
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.config import Config


class SongManager(object):
    def init_song(self):
        # type: () -> None
        if SongFacade.clip_trigger_quantization() == Live.Song.Quantization.q_no_q:
            System.client().show_warning("The global launch quantization is set to None")

        for armed_track in SongFacade.armed_tracks():
            Scheduler.defer(armed_track.unarm)

        startup_track = self._get_startup_track()
        DomainEventBus.notify(SongInitializedEvent())
        if startup_track:
            seq = Sequence()
            seq.add(wait=2)
            seq.add(startup_track.select)
            seq.add(ApplicationView.focus_current_track)
            seq.done()
        Scheduler.wait(2, partial(CommandBus.dispatch, ResetSongCommand()))

    def _get_startup_track(self):
        # type: () -> Optional[AbstractTrack]
        if Config.FOCUS_PROPHET_ON_STARTUP:
            first_prophet_track = next(SongFacade.prophet_tracks(), None)
            if first_prophet_track:
                return first_prophet_track
            else:
                raise Protocol0Warning("Couldn't find prophet track")

        armed_tracks = list(SongFacade.armed_tracks())
        if len(armed_tracks):
            return armed_tracks[0]

        if SongFacade.selected_track() == SongFacade.master_track():
            return next(SongFacade.abstract_tracks())

        return None
