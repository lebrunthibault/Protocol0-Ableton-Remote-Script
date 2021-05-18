from typing import List

from _Framework.SubjectSlot import Subject
from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.tests.fixtures.abstract_group_track import make_external_synth_track
from a_protocol_0.tests.fixtures.simple_track import AbletonTrack, TrackType, make_simple_track
from a_protocol_0.tests.fixtures.song_view import AbletonSongView


class AbletonSong(Subject):
    __subject_events__ = ("is_playing",)

    def __init__(self, tracks, view):
        # type: (List[AbletonTrack], AbletonSongView) -> None
        self.tracks = tracks if tracks else []
        self.return_tracks = []  # type: List[AbletonTrack]
        self.view = view
        self.master_track = SimpleTrack(track=AbletonTrack())  # type: ignore

    def begin_undo_step(self):
        # type: () -> None
        pass

    def end_undo_step(self):
        # type: () -> None
        pass


def make_song(count_simple_tracks=1, count_group_tracks=0):
    # type: (int, int) -> Song
    # noinspection PyTypeChecker
    song = Song(AbletonSong([], AbletonSongView()))
    [make_external_synth_track(song) for _ in range(count_group_tracks)]
    [make_simple_track(song, track_type=TrackType.MIDI) for _ in range(count_simple_tracks)]

    if len(list(song.simple_tracks)):
        song._view.selected_track = list(song.simple_tracks)[0]._track

    return song
