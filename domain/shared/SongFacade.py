from collections import Iterator

from typing import TYPE_CHECKING, Optional, List


if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
    from protocol0.domain.lom.scene.Scene import Scene
    from protocol0.domain.lom.clip.Clip import Clip


class SongFacade(object):
    """ Read only facade for accessing song properties """
    _song = None  # type: Optional[Song]

    @classmethod
    def signature_numerator(cls):
        # type: () -> int
        return cls._song.signature_numerator

    @classmethod
    def selected_track(cls):
        # type: () -> Optional[SimpleTrack]
        return cls._song.selected_track

    @classmethod
    def current_track(cls):
        # type: () -> AbstractTrack
        return cls._song.current_track

    @classmethod
    def simple_tracks(cls):
        # type: () -> Iterator[SimpleTrack]
        return cls._song.simple_tracks

    @classmethod
    def abstract_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return cls._song.abstract_tracks

    @classmethod
    def prophet_tracks(cls):
        # type: () -> Iterator[ExternalSynthTrack]
        return cls._song.prophet_tracks

    @classmethod
    def selected_scene(cls):
        # type: () -> Scene
        return cls._song.selected_scene

    @classmethod
    def playing_scene(cls):
        # type: () -> Optional[Scene]
        return cls._song.playing_scene

    @classmethod
    def looping_scene(cls):
        # type: () -> Optional[Scene]
        return cls._song.looping_scene

    @classmethod
    def scenes(cls):
        # type: () -> List[Scene]
        return cls._song.scenes

    @classmethod
    def selected_clip(cls):
        # type: () -> Optional[Clip]
        return cls._song.selected_clip

    @classmethod
    def is_playing(cls):
        # type: () -> bool
        return cls._song.is_playing

    @classmethod
    def record_mode(cls):
        # type: () -> bool
        return cls._song.record_mode

    @classmethod
    def midi_recording_quantization(cls):
        # type: () -> int
        return cls._song.midi_recording_quantization
