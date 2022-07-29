from typing import Optional

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ResetSongCommand import ResetSongCommand
from protocol0.domain.lom.song.RealSetLoadedEvent import RealSetLoadedEvent
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SongInitService(object):
    _REAL_SET_CLIP_THRESHOLD = 10  # below this, we consider it a test set

    def __init__(self, playback_component):
        # type: (PlaybackComponent) -> None
        self._playback_component = playback_component

    def init_song(self):
        # type: () -> Sequence
        # the song usually starts playing after this method is executed
        CommandBus.dispatch(ResetSongCommand())
        clip_count = len(
                [
                    clip
                    for track in SongFacade.abstract_tracks()
                    for clip in track.clips
                    if not clip.muted
                ]
            )

        if clip_count > self._REAL_SET_CLIP_THRESHOLD:
            DomainEventBus.emit(RealSetLoadedEvent())

        startup_track = self._get_startup_track()
        DomainEventBus.emit(SongInitializedEvent())
        seq = Sequence()
        if startup_track:
            seq.wait(2)
            seq.add(startup_track.select)
            seq.add(ApplicationViewFacade.focus_current_track)

        seq.wait(10)
        seq.add(self._playback_component.reset)

        return seq.done()

    def _get_startup_track(self):
        # type: () -> Optional[AbstractTrack]
        armed_tracks = list(SongFacade.armed_tracks())
        if len(armed_tracks):
            return armed_tracks[0]

        if SongFacade.selected_track() == SongFacade.master_track():
            return next(iter(SongFacade.abstract_tracks()))

        return None
