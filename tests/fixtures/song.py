from typing import List

from _Framework.SubjectSlot import Subject
from protocol0.lom.Song import Song
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.tests.fixtures.simple_track import AbletonTrack, make_simple_track
from protocol0.tests.fixtures.song_view import AbletonSongView


class AbletonSong(Subject):
    __subject_events__ = ("is_playing", "record_mode", "tempo", "midi_recording_quantization")

    def __init__(self, tracks, view):
        # type: (List[AbletonTrack], AbletonSongView) -> None
        self.tracks = tracks if tracks else []
        self.return_tracks = []  # type: List[AbletonTrack]
        self.view = view
        self.master_track = SimpleTrack(track=AbletonTrack(), index=0)  # type: ignore

    def begin_undo_step(self):
        # type: () -> None
        pass

    def end_undo_step(self):
        # type: () -> None
        pass


def make_song(count_simple_tracks=1):
    # type: (int, int) -> Song
    # noinspection PyTypeChecker
    song = Song(AbletonSong([], AbletonSongView()))
    song.parent.songTracksManager._live_track_id_to_simple_track.clear()
    [make_simple_track(song, index=i) for i in range(count_simple_tracks)]

    if len(list(song.simple_tracks)):
        song._view.selected_track = list(song.simple_tracks)[0]._track

    return song
