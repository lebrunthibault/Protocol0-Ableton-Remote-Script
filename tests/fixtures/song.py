from typing import List

from _Framework.SubjectSlot import Subject
from protocol0.domain.lom.song.Song import Song
from protocol0.tests.fixtures.simple_track import AbletonTrack
from protocol0.tests.fixtures.song_view import AbletonSongView


class AbletonSong(Subject):
    __subject_events__ = ("is_playing", "record_mode", "tempo", "midi_recording_quantization", "re_enable_automation_enabled", "tracks")

    def __init__(self, tracks, view):
        # type: (List[AbletonTrack], AbletonSongView) -> None
        self.view = view
        self.tempo = 120

        self.tracks = tracks if tracks else []
        self.return_tracks = []  # type: List[AbletonTrack]
        self.master_track = AbletonTrack()  # type: ignore
        self.view.selected_track = self.master_track

    def begin_undo_step(self):
        # type: () -> None
        pass

    def end_undo_step(self):
        # type: () -> None
        pass


def patch_song():
    # type: () -> None
    Song.get_instance()._song = AbletonSong([], AbletonSongView())
