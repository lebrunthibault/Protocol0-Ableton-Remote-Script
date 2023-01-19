from collections import namedtuple

from _Framework.SubjectSlot import Subject
from typing import List, Any

from protocol0.tests.domain.fixtures.scene import AbletonScene
from protocol0.tests.domain.fixtures.simple_track import AbletonTrack, TrackType
from protocol0.tests.domain.fixtures.song_view import AbletonSongView


class AbletonSong(Subject):
    __subject_events__ = (
        "is_playing",
        "record_mode",
        "tempo",
        "clip_trigger_quantization",
        "midi_recording_quantization",
        "re_enable_automation_enabled",
        "tracks",
        "visible_tracks",
        "scenes",
        "current_song_time",
    )

    def __init__(self):
        # type: () -> None
        self.view = AbletonSongView()
        self.tempo = 120
        self.signature_numerator = 4

        first_track = AbletonTrack()
        first_track.name = "First"
        self.tracks = [first_track]
        self.visible_tracks = self.tracks
        self.return_tracks = []  # type: List[AbletonTrack]
        self.master_track = AbletonTrack(track_type=TrackType.AUDIO)
        self.master_track.name = "Master"
        self.scenes = [AbletonScene()]
        self.clip_trigger_quantization = 0

        self.view.selected_track = self.tracks[0]
        self.view.selected_scene = self.scenes[0]
        self.is_playing = False

    def __repr__(self):
        # type: () -> str
        return

    def stop_playing(self):
        # type: () -> None
        pass

    def stop_all_clips(self, _):
        # type: (bool) -> None
        pass

    def get_current_beats_song_time(self):
        # type: () -> namedtuple
        beats_song_time = namedtuple("beats_song_time", ["bars", "beats", "sub_division", "ticks"])
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

    def create_midi_track(self, _):
        # type: (int) -> None
        pass

    def create_audio_track(self, _):
        # type: (int) -> None
        pass

    def duplicate_track(self, _):
        # type: (int) -> None
        pass

    def delete_track(self, _):
        # type: (int) -> None
        pass

    def create_scene(self, _):
        # type: (int) -> None
        pass

    def duplicate_scene(self, _):
        # type: (int) -> None
        pass

    def delete_scene(self, _):
        # type: (int) -> None
        pass
