from functools import partial

from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.TrackRepository import TrackRepository
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class TrackPlayerService(object):
    def __init__(self, song, track_repository):
        # type: (Song, TrackRepository) -> None
        self._song = song
        self._track_repository = track_repository

    def toggle_track(self, track_name):
        # type: (str) -> None
        track = self._track_repository.find_simple_by_name(track_name)

        if len(track.clips) == 0:
            raise Protocol0Warning("%s has no clips" % track)

        self._toggle_track_first_clip(track)

    def _toggle_track_first_clip(self, track):
        # type: (SimpleTrack) -> None
        if len(track.clips) == 0:
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

    def toggle_drums(self):
        # type: () -> None
        group_track = self._track_repository.find_group_by_name(Config.DRUMS_TRACK_NAME)
        drum_tracks = self._track_repository.find_all_simple_sub_tracks(group_track)
        if any(track for track in drum_tracks if track.is_playing):
            for track in drum_tracks:
                track.stop()
        else:
            song_is_playing = SongFacade.is_playing()
            for track in drum_tracks:
                self._toggle_track_first_clip(track)

                # when the song is not playing clips are not starting at the same time
                if not song_is_playing:
                    self._song.stop_playing()
                    Scheduler.defer(self._song.start_playing)

