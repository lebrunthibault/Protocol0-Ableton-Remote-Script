from functools import partial

from typing import Dict, Any, Optional

from protocol0.domain.lom.device.DrumRackLoadedEvent import DrumRackLoadedEvent
from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack
from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrackNameUpdatedEvent import (
    AbstractTrackNameUpdatedEvent,
)
from protocol0.domain.lom.track.simple_track.MasterTrackMuteToggledEvent import \
    MasterTrackMuteToggledEvent
from protocol0.domain.lom.track.simple_track.MasterTrackRoomEqToggledEvent import (
    MasterTrackRoomEqToggledEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrackFirstClipAddedEvent import (
    SimpleTrackFirstClipAddedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrackLastClipDeletedEvent import (
    SimpleTrackLastClipDeletedEvent,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SongState(object):
    def __init__(self, set_id):
        # type: (str) -> None
        self._cache = {}  # type: Dict[str, Any]

        self._id = set_id
        self._title = None  # type: Optional[str]

        listened_events = [
            TracksMappedEvent,
            AbstractTrackNameUpdatedEvent,
            SimpleTrackFirstClipAddedEvent,
            SimpleTrackLastClipDeletedEvent,
            SelectedTrackChangedEvent,
            DrumRackLoadedEvent,
            MasterTrackRoomEqToggledEvent,
            MasterTrackMuteToggledEvent
        ]

        for event in listened_events:
            DomainEventBus.subscribe(event, lambda _: self.notify())

    def to_dict(self):
        # type: () -> Dict
        room_eq = SongFacade.master_track() and SongFacade.master_track().room_eq
        muted = SongFacade.master_track() is not None and SongFacade.master_track().muted

        return {
            "id": self._id,
            "title": self._title,
            "muted": muted,
            "drum_rack_visible": isinstance(
                SongFacade.selected_track().instrument, InstrumentDrumRack
            ),
            "room_eq_enabled": room_eq is not None and room_eq.is_active,
        }

    def notify(self, force=False):
        # type: (bool) -> None
        data = self.to_dict()
        if self._cache != data or force:
            seq = Sequence()
            seq.add(partial(Backend.client().notify_song_state, data))

            if self._title is None:
                seq.wait_for_backend_response()
                seq.add(lambda: setattr(self, "_title", seq.res["title"]))  # type: ignore[index]

            seq.done()

        self._cache = data
