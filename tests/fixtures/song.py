import pytest
from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.groupTrack import make_group_ex_track
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.songView import AbletonSongView
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.simpleTrack import make_simpler_track, make_group_track


class AbletonSong:
    def __init__(self, tracks, view):
        self.tracks = tracks if tracks else []
        self.view = view


def select_song_track(song, index):
    # type: (Song, int) -> None
    if index < 1 or index > len(song.tracks):
        raise Exception("invalid index for select_song_track")
    song.view.selected_track = song.tracks[index - 1].track


def make_song(count_group_tracks=0, count_simple_tracks=0):
    # type: (int, int) -> Song
    song = Song(AbletonSong([], AbletonSongView()))
    [make_group_ex_track(song) for _ in range(count_group_tracks)]
    [make_simpler_track(song) for _ in range(count_simple_tracks)]

    if len(song.tracks):
        song.view.selected_track = song.tracks[0].track

    song.set_selected_track = select_song_track

    return song


@pytest.fixture()
def base_song():
    # type: () -> Song
    song = Song(AbletonSong([], AbletonSongView()))
    make_group_ex_track(song, TrackName.GROUP_PROPHET_NAME)
    make_group_ex_track(song, TrackName.GROUP_MINITAUR_NAME)
    make_group_track(song, "drums")
    make_simpler_track(song, "kicks - 0")
    make_simpler_track(song, "snares - 0")

    song.view.selected_track = song.tracks[0].track

    return song