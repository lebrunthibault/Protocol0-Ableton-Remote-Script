from typing import Dict, Any

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DrumRackLoadedEvent import DrumRackLoadedEvent
from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack
from protocol0.domain.lom.instrument.instrument.InstrumentSimpler import InstrumentSimpler
from protocol0.domain.lom.instrument.preset.preset_importer.DirectoryPresetImporter import DirectoryPresetImporter
from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrackNameUpdatedEvent import AbstractTrackNameUpdatedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackFirstClipAddedEvent import SimpleTrackFirstClipAddedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackLastClipDeletedEvent import SimpleTrackLastClipDeletedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade


class SongState(object):
    def __init__(self):
        # type: () -> None
        DomainEventBus.subscribe(TracksMappedEvent, lambda _: self.notify())
        DomainEventBus.subscribe(AbstractTrackNameUpdatedEvent, lambda _: self.notify())
        DomainEventBus.subscribe(SimpleTrackFirstClipAddedEvent, lambda _: self.notify())
        DomainEventBus.subscribe(SimpleTrackLastClipDeletedEvent, lambda _: self.notify())
        DomainEventBus.subscribe(SelectedTrackChangedEvent, lambda _: self.notify())
        DomainEventBus.subscribe(DrumRackLoadedEvent, lambda _: self.notify())
        presets = DirectoryPresetImporter(InstrumentSimpler.PRESETS_PATH,
                                          InstrumentSimpler.PRESET_EXTENSION).import_presets()
        drum_categories = set()
        for preset in presets:
            drum_categories.add(preset.category)
        self._drum_categories = sorted(drum_categories)
        self._cache = {}  # type: Dict[str, Any]

    def to_dict(self):
        # type: () -> Dict
        drum_track_names = []
        if SongFacade.drums_track():
            drum_track_names = [track.name for track in SongFacade.drums_track().get_all_simple_sub_tracks() if
                                len(track.clips)]
        return {
            "drum_track_names": drum_track_names,
            "drum_categories": self._drum_categories,
            "favorite_device_names": [device.name for device in DeviceEnum.favorites()],
            "drum_rack_visible": isinstance(SongFacade.selected_track().instrument, InstrumentDrumRack)
        }

    def notify(self, force=False):
        # type: (bool) -> None
        data = self.to_dict()
        if self._cache != data or force:
            Backend.client().notify_song_state(data)

        self._cache = data
