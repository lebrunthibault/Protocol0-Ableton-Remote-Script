from functools import partial

import Live
from typing import Optional, Type

from protocol0.domain.lom.device.DrumRackService import DrumRackService
from protocol0.domain.lom.sample.SampleCategory import SampleCategory
from protocol0.domain.lom.sample.SampleCategoryEnum import SampleCategoryEnum
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.audio.special.ResamplingTrack import ResamplingTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.midi.special.UsamoTrack import UsamoTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class TrackFactory(object):
    def __init__(self, track_crud_component, browser_service, drum_rack_service):
        # type: (TrackCrudComponent, BrowserServiceInterface, DrumRackService) -> None
        self._track_crud_component = track_crud_component
        self._browser_service = browser_service
        self._drum_rack_service = drum_rack_service

    def create_simple_track(self, track, index, cls=None):
        # type: (Live.Track.Track, int, Optional[Type[SimpleTrack]]) -> SimpleTrack
        # checking first on existing tracks
        existing_simple_track = Song.optional_simple_track_from_live_track(track)
        if existing_simple_track and (cls is None or isinstance(existing_simple_track, cls)):
            # reindexing tracks
            existing_simple_track._index = index
            return existing_simple_track

        special_tracks = (UsamoTrack, ResamplingTrack)

        if cls is None:
            if track.has_midi_input:
                cls = SimpleMidiTrack
            elif track.has_audio_input:
                cls = SimpleAudioTrack

            for special_track in special_tracks:
                if track.name == special_track.TRACK_NAME:  # type: ignore[attr-defined]
                    cls = special_track  # type: ignore

            if cls is None:
                raise Protocol0Error("Unknown track type")

        return cls(track, index)

    def create_abstract_group_track(self, base_group_track):
        # type: (SimpleTrack) -> AbstractGroupTrack
        previous_abstract_group_track = base_group_track.abstract_group_track

        if ExternalSynthTrack.is_group_track_valid(base_group_track):
            if isinstance(previous_abstract_group_track, ExternalSynthTrack):
                return previous_abstract_group_track
            else:
                return ExternalSynthTrack(base_group_track=base_group_track)

        # handling normal group track

        if isinstance(previous_abstract_group_track, NormalGroupTrack):
            return previous_abstract_group_track
        else:
            return NormalGroupTrack.make(base_group_track)

    def add_sample_track(self, category, sample_sub_category):
        # type: (SampleCategoryEnum, str) -> Sequence
        sample_group_track = Song.drums_track()
        if sample_group_track is None:
            raise Protocol0Warning("Sample group track doesn't exist")

        if sample_sub_category.lower() not in category.subcategories:
            raise Protocol0Warning("Cannot find %s sample category for '%s'" % (category, sample_sub_category))

        sample_category = SampleCategory(category, sample_sub_category)

        sample_group_track.base_track.is_folded = False

        seq = Sequence()
        seq.add(
            partial(self._track_crud_component.create_midi_track, sample_category.create_track_index)
        )
        seq.add(lambda: setattr(Song.selected_track(), "volume", -15))
        seq.add(lambda: setattr(Song.selected_track(), "color", sample_category.color))

        # not creating clip here
        seq.add(partial(self._drum_rack_service.load_category_drum_rack, sample_category))

        return seq.done()
