import pytest
from typing import List

from a_protocol_0.devices.InstrumentMinitaur import InstrumentMinitaur
from a_protocol_0.devices.InstrumentProphet import InstrumentProphet
from a_protocol_0.lom.Song import Song
from a_protocol_0.tests.fixtures.groupTrack import make_external_synth_track
from a_protocol_0.tests.fixtures.simpleTrack import make_simpler_track, make_group_track, \
    AbletonTrack
from a_protocol_0.tests.fixtures.songView import AbletonSongView


class AbletonSong(object):
    def __init__(self, tracks, view):
        # type: (List[AbletonTrack], AbletonSongView) -> None
        self.tracks = tracks if tracks else []
        self.view = view
        self.master_track = None


def select_song_track(song, index):
    # type: (Song, int) -> None
    if index < 1 or index > len(song.simple_tracks):
        raise Exception("invalid index for select_song_track")
    song._view.selected_track = song.simple_tracks[index - 1]._track


def make_song(count_group_tracks=0, count_simple_tracks=0):
    # type: (int, int) -> Song
    # noinspection PyTypeChecker
    song = Song(AbletonSong([], AbletonSongView()))
    [make_external_synth_track(song) for _ in range(count_group_tracks)]
    [make_simpler_track(song) for _ in range(count_simple_tracks)]

    if len(song.simple_tracks):
        song._view.selected_track = song.simple_tracks[0]._track

    song.set_selected_track = select_song_track

    return song


@pytest.fixture()
def base_song():
    # type: () -> Song
    # noinspection PyTypeChecker
    song = Song(AbletonSong([], AbletonSongView()))
    make_external_synth_track(song, InstrumentProphet.NAME)
    make_external_synth_track(song, InstrumentMinitaur.NAME)
    make_group_track(song, "drums")
    make_simpler_track(song, "kicks - 0")
    make_simpler_track(song, "snares - 0")

    song._view.selected_track = song.simple_tracks[0]._track

    return song
