from collections import Iterator

from typing import TYPE_CHECKING, Optional, List

import Live


if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
    from protocol0.domain.lom.scene.Scene import Scene
    from protocol0.domain.lom.clip.Clip import Clip
    from protocol0.domain.lom.clip.MidiClip import MidiClip
    from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
    from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter


class SongFacade(object):
    """ Read only facade for accessing song properties """
    @classmethod
    def _song(cls):
        # type: () -> Song
        from protocol0 import Protocol0

        return Protocol0.CONTAINER.song

    @classmethod
    def live_song(cls):
        # type: () -> Live.Song.Song
        return cls._song()._song

    @classmethod
    def signature_numerator(cls):
        # type: () -> int
        return cls._song().signature_numerator

    @classmethod
    def selected_track(cls):
        # type: () -> Optional[SimpleTrack]
        return cls._song().selected_track

    @classmethod
    def current_track(cls):
        # type: () -> AbstractTrack
        return cls._song().current_track

    @classmethod
    def current_external_synth_track(cls):
        # type: () -> ExternalSynthTrack
        return cls._song().current_external_synth_track

    @classmethod
    def abstract_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return cls._song().abstract_tracks

    @classmethod
    def simple_tracks(cls):
        # type: () -> Iterator[SimpleTrack]
        return cls._song().simple_tracks

    @classmethod
    def external_synth_tracks(cls):
        # type: () -> Iterator[ExternalSynthTrack]
        return cls._song().external_synth_tracks

    @classmethod
    def scrollable_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return cls._song().scrollable_tracks

    @classmethod
    def visible_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return cls._song().visible_tracks

    @classmethod
    def prophet_tracks(cls):
        # type: () -> Iterator[ExternalSynthTrack]
        return cls._song().prophet_tracks

    @classmethod
    def master_track(cls):
        # type: () -> Optional[SimpleTrack]
        return cls._song().master_track

    @classmethod
    def selected_scene(cls):
        # type: () -> Scene
        return cls._song().selected_scene

    @classmethod
    def playing_scene(cls):
        # type: () -> Optional[Scene]
        return cls._song().playing_scene

    @classmethod
    def looping_scene(cls):
        # type: () -> Optional[Scene]
        return cls._song().looping_scene

    @classmethod
    def last_manually_started_scene(cls):
        # type: () -> Scene
        return cls._song().last_manually_started_scene

    @classmethod
    def scenes(cls):
        # type: () -> List[Scene]
        return cls._song().scenes

    @classmethod
    def highlighted_clip_slot(cls):
        # type: () -> Optional[ClipSlot]
        return cls._song().highlighted_clip_slot

    @classmethod
    def selected_clip(cls):
        # type: () -> Optional[Clip]
        return cls._song().selected_clip

    @classmethod
    def selected_midi_clip(cls):
        # type: () -> MidiClip
        clip = cls._song().selected_clip
        assert isinstance(clip, MidiClip), "expected midi clip"
        return clip

    @classmethod
    def selected_parameter(cls):
        # type: () -> Optional[DeviceParameter]
        return cls._song().selected_parameter

    @classmethod
    def is_playing(cls):
        # type: () -> bool
        return cls._song().is_playing

    @classmethod
    def record_mode(cls):
        # type: () -> bool
        return cls._song().record_mode

    @classmethod
    def midi_recording_quantization(cls):
        # type: () -> int
        return cls._song().midi_recording_quantization

    @classmethod
    def tempo(cls):
        # type: () -> float
        return cls._song().tempo
