from collections import Iterator

from typing import TYPE_CHECKING, Optional, List, cast

import Live
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.ScenesService import SongScenesService
    from protocol0.domain.lom.track.TracksService import SongTracksService
    from protocol0.domain.lom.song.Song import Song
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
    from protocol0.domain.lom.scene.Scene import Scene
    from protocol0.domain.lom.clip.Clip import Clip
    from protocol0.domain.lom.clip.MidiClip import MidiClip
    from protocol0.domain.lom.clip.AudioClip import AudioClip
    from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
    from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
    from protocol0.domain.lom.instrument.instrument.InstrumentProphet import InstrumentProphet
    from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter


# noinspection PyArgumentList
class SongFacade(object):
    """ Read only facade for accessing song properties """
    _INSTANCE = None  # type: Optional[SongFacade]

    def __init__(self, song, song_tracks_service, song_scenes_service):
        # type: (Song, SongTracksService, SongScenesService) -> None
        SongFacade._INSTANCE = self
        self._song = song
        self._song_tracks_service = song_tracks_service
        self._song_scenes_service = song_scenes_service

    @classmethod
    def live_song(cls):
        # type: () -> Live.Song.Song
        return cls._INSTANCE._song._song

    @classmethod
    def live_tracks(cls):
        # type: () -> Iterator[Live.Track.Track]
        return (track for track in
                list(cls.live_song().tracks) + list(cls.live_song().return_tracks) + [cls.live_song().master_track])

    @classmethod
    def signature_numerator(cls):
        # type: () -> int
        return cls.live_song().signature_numerator

    @classmethod
    def selected_track(cls):
        # type: () -> Optional[SimpleTrack]
        return cls.optional_simple_track_from_live_track(cls.live_song().view.selected_track)

    @classmethod
    def current_track(cls):
        # type: () -> AbstractTrack
        return cls.selected_track().abstract_track

    @classmethod
    def current_external_synth_track(cls):
        # type: () -> ExternalSynthTrack
        from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack

        if isinstance(SongFacade.current_track(), ExternalSynthTrack):
            return cast(ExternalSynthTrack, SongFacade.current_track())
        else:
            raise Protocol0Warning("current track is not an ExternalSynthTrack")

    @classmethod
    def abstract_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return cls._INSTANCE._song.abstract_tracks

    @classmethod
    def simple_track_from_live_track(cls, live_track):
        # type: (Live.Track.Track) -> SimpleTrack
        """ we use the live ptr instead of the track to be able to access outdated simple tracks on deletion """
        return cls._INSTANCE._song_tracks_service._live_track_id_to_simple_track[live_track._live_ptr]

    @classmethod
    def optional_simple_track_from_live_track(cls, live_track):
        # type: (Live.Track.Track) -> Optional[SimpleTrack]
        try:
            return cls.simple_track_from_live_track(live_track)
        except KeyError:
            return None

    @classmethod
    def simple_tracks(cls):
        # type: () -> Iterator[SimpleTrack]
        return (track for track in cls.all_simple_tracks() if track.IS_ACTIVE)

    @classmethod
    def all_simple_tracks(cls):
        # type: () -> Iterator[SimpleTrack]
        return (track for track in cls._INSTANCE._song_tracks_service._live_track_id_to_simple_track.values())

    @classmethod
    def external_synth_tracks(cls):
        # type: () -> Iterator[ExternalSynthTrack]
        from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack

        for track in cls.abstract_tracks():
            if isinstance(track, ExternalSynthTrack):
                yield track

    @classmethod
    def scrollable_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return cls._INSTANCE._song.scrollable_tracks

    @classmethod
    def visible_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return (t for t in cls.simple_tracks() if t.is_visible)

    @classmethod
    def armed_tracks(cls):
        # type: () -> Iterator[AbstractTrack]
        return (track for track in cls.abstract_tracks() if track.is_armed)

    @classmethod
    def prophet_tracks(cls):
        # type: () -> Iterator[ExternalSynthTrack]
        for track in cls.external_synth_tracks():
            if isinstance(track.instrument, InstrumentProphet):
                yield track

    @classmethod
    def usamo_track(cls):
        # type: () -> Optional[SimpleTrack]
        return cls._INSTANCE._song_tracks_service._usamo_track

    @classmethod
    def master_track(cls):
        # type: () -> Optional[SimpleTrack]
        return cls._INSTANCE._song_tracks_service._master_track

    @classmethod
    def selected_scene(cls):
        # type: () -> Scene
        return cls._INSTANCE._song_scenes_service.get_scene(cls.live_song().view.selected_scene)

    @classmethod
    def playing_scene(cls):
        # type: () -> Optional[Scene]
        from protocol0.domain.lom.scene.Scene import Scene

        return Scene.PLAYING_SCENE

    @classmethod
    def looping_scene(cls):
        # type: () -> Optional[Scene]
        from protocol0.domain.lom.scene.Scene import Scene

        return Scene.LOOPING_SCENE

    @classmethod
    def last_manually_started_scene(cls):
        # type: () -> Scene
        from protocol0.domain.lom.scene.Scene import Scene

        return Scene.LAST_MANUALLY_STARTED_SCENE or cls.selected_scene()

    @classmethod
    def scenes(cls):
        # type: () -> List[Scene]
        return cls._INSTANCE._song_scenes_service.scenes

    @classmethod
    def highlighted_clip_slot(cls):
        # type: () -> Optional[ClipSlot]
        if cls.selected_track() is None:
            return None
        else:
            return next((cs for cs in cls.selected_track().clip_slots if cs._clip_slot == cls.live_song().view.highlighted_clip_slot),
                        None)

    @classmethod
    def selected_clip(cls):
        # type: () -> Clip
        clip = cls.highlighted_clip_slot() and cls.highlighted_clip_slot().clip
        if clip is None:
            raise Protocol0Warning("no selected midi clip")
        return clip

    @classmethod
    def selected_optional_clip(cls):
        # type: () -> Optional[Clip]
        return cls.highlighted_clip_slot() and cls.highlighted_clip_slot().clip

    @classmethod
    def selected_midi_clip(cls):
        # type: () -> MidiClip
        clip = cls._INSTANCE._song.selected_clip
        if not isinstance(clip, MidiClip):
            raise Protocol0Warning("no selected midi clip")
        return clip

    @classmethod
    def template_dummy_clip(cls):
        # type: () -> Optional[AudioClip]
        return cls._INSTANCE._song_tracks_service._template_dummy_clip

    @classmethod
    def current_instrument(cls):
        # type: () -> InstrumentInterface
        instrument = cls.current_track().instrument
        if instrument is None:
            raise Protocol0Warning("current track has no instrument")
        return instrument

    @classmethod
    def selected_parameter(cls):
        # type: () -> Optional[DeviceParameter]
        return cls._INSTANCE._song.selected_parameter

    @classmethod
    def is_playing(cls):
        # type: () -> bool
        return cls._INSTANCE._song.is_playing

    @classmethod
    def record_mode(cls):
        # type: () -> bool
        return cls._INSTANCE._song.record_mode

    @classmethod
    def midi_recording_quantization(cls):
        # type: () -> int
        return cls._INSTANCE._song.midi_recording_quantization

    @classmethod
    def tempo(cls):
        # type: () -> float
        return cls._INSTANCE._song.tempo

    @classmethod
    def current_beats_song_time(cls):
        # type: () -> Live.Song.BeatTime
        return cls.live_song().get_current_beats_song_time()

    @classmethod
    def clip_trigger_quantization(cls):
        # type: () -> int
        return cls._INSTANCE._song.clip_trigger_quantization