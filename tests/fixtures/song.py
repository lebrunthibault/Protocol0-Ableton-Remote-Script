from typing import List

from _Framework.SubjectSlot import Subject
from a_protocol_0.lom.Song import Song
from a_protocol_0.tests.fixtures.group_track import make_external_synth_track
from a_protocol_0.tests.fixtures.simple_track import make_simpler_track, AbletonTrack
from a_protocol_0.tests.fixtures.song_view import AbletonSongView


class AbletonSong(Subject):
    __subject_events__ = ("is_playing",)

    def __init__(self, tracks, view):
        # type: (List[AbletonTrack], AbletonSongView) -> None
        self.tracks = tracks if tracks else []
        self.view = view
        self.master_track = None


def make_song(count_group_tracks=0, count_simple_tracks=0):
    # type: (int, int) -> Song
    # noinspection PyTypeChecker
    song = Song(AbletonSong([], AbletonSongView()))
    [make_external_synth_track(song) for _ in range(count_group_tracks)]
    [make_simpler_track(song) for _ in range(count_simple_tracks)]

    if len(song.simple_tracks):
        song._view.selected_track = song.simple_tracks[0]._track

    return song
