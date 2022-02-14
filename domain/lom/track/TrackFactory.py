from typing import Optional, Type, TYPE_CHECKING

import Live
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackFactory(object):
    def __init__(self, song):
        # type: (Song) -> None
        self._song = song

    def create_simple_track(self, track, index, cls=None):
        # type: (Live.Track.Track, int, Optional[Type[SimpleTrack]]) -> SimpleTrack
        # checking first on existing tracks
        existing_simple_track = SongFacade.optional_simple_track_from_live_track(track)
        if existing_simple_track and (cls is None or isinstance(existing_simple_track, cls)):
            return existing_simple_track

        if cls is None:
            if track.name == SimpleInstrumentBusTrack.DEFAULT_NAME:
                cls = SimpleInstrumentBusTrack
            elif track.has_midi_input:
                cls = SimpleMidiTrack
            elif track.has_audio_input:
                cls = SimpleAudioTrack
            else:
                raise Protocol0Error("Unknown track type")

        return cls(track=track, index=index)

    def create_abstract_group_track(self, base_group_track):
        # type: (SimpleTrack) -> AbstractGroupTrack
        if self._is_valid_external_synth_track(base_group_track):
            return self._create_external_synth_track(base_group_track=base_group_track)

        # handling normal group track
        previous_abstract_group_track = base_group_track.abstract_group_track

        if isinstance(previous_abstract_group_track, NormalGroupTrack):
            return previous_abstract_group_track
        else:
            return NormalGroupTrack(base_group_track=base_group_track)

    def _create_external_synth_track(self, base_group_track):
        # type: (SimpleTrack) -> ExternalSynthTrack
        """ discarding automated tracks in creation / suppression """
        midi_track = base_group_track.sub_tracks[0]

        if not midi_track.instrument:
            midi_track.instrument = InstrumentMinitaur(track=midi_track, device=None)

        if isinstance(base_group_track.abstract_group_track, ExternalSynthTrack):
            return base_group_track.abstract_group_track
        else:
            return ExternalSynthTrack(base_group_track=base_group_track)

    def _is_valid_external_synth_track(self, base_group_track):
        # type: (SimpleTrack) -> bool
        if len(base_group_track.sub_tracks) < 2:
            return False

        if not isinstance(base_group_track.sub_tracks[0], SimpleMidiTrack):
            return False
        if not isinstance(base_group_track.sub_tracks[1], SimpleAudioTrack):
            return False

        for track in base_group_track.sub_tracks[2:]:
            if not isinstance(track, SimpleAudioTrack):
                return False

        return True
