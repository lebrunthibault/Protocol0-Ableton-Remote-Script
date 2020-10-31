from ...lom.Song import Song
from .songView import AbletonSongView
from .simpleTrack import make_simpler_track


class AbletonSong:
    def __init__(self, tracks, view):
        self.tracks = tracks if tracks else []
        self.view = view

def make_song(count_simple_tracks = 0):
    # type: (int) -> Song
    song = Song(AbletonSong([], AbletonSongView()))
    simpler_tracks = [make_simpler_track(song, i + 1) for i in range(count_simple_tracks)]
    tracks = simpler_tracks
    song.tracks = tracks

    if len(song.tracks):
        song.view.selected_track = tracks[0].track

    return song


def select_song_track(song, index):
    # type: (Song, int) -> None
    if index < 1 or index > len(song.tracks):
        raise Exception("invalid index for select_song_track")
    song.view.selected_track = song.tracks[index - 1].track
