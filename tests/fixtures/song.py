from collections import namedtuple

from _Framework.SubjectSlot import Subject
from typing import List, Any

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

    def __init__(self):
        # type: () -> None
        self.view = AbletonSongView()
        self.tempo = 120
        self.signature_numerator = 4

        self.tracks = [self.view.selected_track]
        self.return_tracks = []  # type: List[AbletonTrack]
        self.master_track = AbletonTrack()  # type: ignore
        self.scenes = [self.view.selected_scene]
        self.clip_trigger_quantization = 0
        self.view.selected_track = self.master_track
        self.is_playing = False

    def stop_playing(self):
        # type: () -> None
        pass

    def stop_all_clips(self, _):
        # type: (bool) -> None
        pass

    def get_current_beats_song_time(self):
        # type: () -> namedtuple
        beats_song_time = namedtuple('beats_song_time', ['bars', 'beats', 'sub_division', 'ticks'])
        return beats_song_time(1, 1, 1, 1)

    def get_data(self, _, default):
        # type: () -> Any
        return default

    def set_data(self, _, __):
        # type: (str, Any) -> None
        pass

    def begin_undo_step(self):
        # type: () -> None
        pass

    def end_undo_step(self):
        # type: () -> None
        pass
