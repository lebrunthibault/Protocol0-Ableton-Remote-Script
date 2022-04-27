from functools import partial

import Live
from typing import Optional, Type, TYPE_CHECKING

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DrumRackService import DrumRackService
from protocol0.domain.lom.drum.DrumCategory import DrumCategory
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackFactory(object):
    def __init__(self, song, browser_service, drum_rack_service):
        # type: (Song, BrowserServiceInterface, DrumRackService) -> None
        self._song = song
        self._browser_service = browser_service
        self._drum_rack_service = drum_rack_service

    def create_simple_track(self, track, index, cls=None):
        # type: (Live.Track.Track, int, Optional[Type[SimpleTrack]]) -> SimpleTrack
        # checking first on existing tracks
        existing_simple_track = SongFacade.optional_simple_track_from_live_track(track)
        if existing_simple_track and (cls is None or isinstance(existing_simple_track, cls)):
            # re indexing tracks
            existing_simple_track._index = index
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

    def add_drum_track(self, name, device_enum=DeviceEnum.SIMPLER):
        # type: (str, DeviceEnum) -> Sequence
        assert device_enum in (DeviceEnum.SIMPLER, DeviceEnum.DRUM_RACK)

        drum_track = SongFacade.drums_track()
        if drum_track is None:
            raise Protocol0Warning("Drum track doesn't exist")

        if name.lower() not in DrumCategory.all():
            raise Protocol0Warning("Cannot fin category for drum track %s" % name)

        drum_category = DrumCategory(name)

        drum_track.is_folded = False

        selected_scene_index = SongFacade.selected_scene().index
        seq = Sequence()
        seq.add(partial(self._song.create_midi_track, drum_category.create_track_index))
        seq.add(lambda: setattr(SongFacade.selected_track(), "volume", -15))

        if device_enum == DeviceEnum.SIMPLER:
            seq.defer()
            seq.add(partial(self._browser_service.load_device_from_enum, device_enum))
            seq.add(partial(self._on_simpler_drum_track_added, drum_category))
            seq.add(lambda: SongFacade.selected_track().clip_slots[selected_scene_index].create_clip())
        elif device_enum == DeviceEnum.DRUM_RACK:
            # not creating clip here
            seq.add(partial(self._drum_rack_service.load_category_drum_rack, drum_category))

        return seq.done()

    def _on_simpler_drum_track_added(self, drum_category):
        # type: (DrumCategory) -> None
        SongFacade.selected_track().instrument.preset_list.set_selected_category(drum_category.name)
        SongFacade.selected_track().instrument.scroll_presets(True)
