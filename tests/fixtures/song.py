from typing import List, Any

from _Framework.SubjectSlot import Subject
from protocol0.tests.fixtures.simple_track import AbletonTrack
from protocol0.tests.fixtures.song_view import AbletonSongView


class AbletonSong(Subject):
    __subject_events__ = (
        "is_playing",
        "record_mode",
        "tempo",
        "midi_recording_quantization",
        "re_enable_automation_enabled",
        "tracks",
        "visible_tracks",
        "scenes",
        "current_song_time"
    )

    def __init__(self, tracks, view):
        # type: (List[AbletonTrack], AbletonSongView) -> None
        self.view = view
        self.tempo = 120

        self.tracks = tracks
        self.return_tracks = []  # type: List[AbletonTrack]
        self.master_track = AbletonTrack()  # type: ignore
        self.scenes = []
        self.clip_trigger_quantization = 0
        self.view.selected_track = self.master_track

    def stop_playing(self):
        # type: () -> None
        pass

    def get_data(self, _, default):
        # type: () -> Any
        return default

    def set_data(self):
        # type: () -> None
        pass

    def begin_undo_step(self):
        # type: () -> None
        pass

    def end_undo_step(self):
        # type: () -> None
        pass
