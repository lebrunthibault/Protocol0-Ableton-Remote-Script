from functools import partial

import Live
from typing import Optional, Type, TYPE_CHECKING

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
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
    def __init__(self, song, browser_service):
        # type: (Song, BrowserServiceInterface) -> None
        self._song = song
        self._browser_service = browser_service

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
        if ExternalSynthTrack.is_group_track_valid(base_group_track):
            return self._create_external_synth_track(base_group_track=base_group_track)

        # handling normal group track
        previous_abstract_group_track = base_group_track.abstract_group_track

        if isinstance(previous_abstract_group_track, NormalGroupTrack):
            return previous_abstract_group_track
        else:
            return NormalGroupTrack.make(base_group_track)

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

    def add_drum_track(self, name):
        # type: (str) -> Sequence
        drum_track = SongFacade.drums_track()
        if drum_track is None:
            raise Protocol0Warning("Drum track doesn't exist")

        name = name.lower()
        if name not in drum_track.categories:
            raise Protocol0Warning("Cannot fin category for drum track %s" % name)

        drum_track.is_folded = False

        selected_scene_index = SongFacade.selected_scene().index
        seq = Sequence()
        seq.add(partial(self._song.create_midi_track, drum_track.sub_tracks[-1].index))
        seq.add(partial(self._browser_service.load_device_from_enum, DeviceEnum.SIMPLER.name))
        seq.defer()
        seq.add(partial(self._on_track_added, name, selected_scene_index))
        return seq.done()

    def _on_track_added(self, name, selected_scene_index):
        # type: (str, int) -> None
        SongFacade.selected_track().volume -= 15
        SongFacade.selected_track().instrument.preset_list.set_selected_category(name)
        SongFacade.selected_track().instrument.scroll_presets(True)
        SongFacade.selected_track().clip_slots[selected_scene_index].create_clip()
