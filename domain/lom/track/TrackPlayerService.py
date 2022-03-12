from functools import partial

from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.TrackRepository import TrackRepository
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class TrackPlayerService(object):
    def __init__(self, track_repository):
        # type: (TrackRepository) -> None
        self._track_repository = track_repository

    def toggle_track(self, track_name):
        # type: (str) -> None
        track = self._track_repository.get_by_name(track_name)
        if track is None:
            Backend.client().show_warning("Couldn't find track %s" % track_name)
            return

        if len(track.clips) == 0:
            Backend.client().show_warning("%s has no clips" % track)
            return

        if track.is_playing:
            Logger.log_info("Stopping %s" % track)
            track.stop()
        else:
            Logger.log_info("Playing %s" % track)

            seq = Sequence()
            clip = next((clip for clip in track.clips if not clip.muted), None)
            if not clip:
                clip = track.clips[0]
                clip.muted = False
                DomainEventBus.one(SongStoppedEvent, partial(setattr, clip, "muted", True))
                seq.defer()

            seq.add(clip.fire)
            seq.done()
