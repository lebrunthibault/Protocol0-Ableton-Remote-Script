from functools import partial
from uuid import uuid4

from typing import Dict, Any, Optional

from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
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


class AbletonSet(object):
    def __init__(self):
        # type: () -> None
        self._cache = {}  # type: Dict[str, Any]

        self._title = None  # type: Optional[str]
        self._id = str(uuid4())
        self.active = True

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

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

    def get_id(self):
        # type: () -> str
        return self._id

    def to_dict(self):
        # type: () -> Dict
        room_eq = SongFacade.master_track() and SongFacade.master_track().room_eq
        muted = SongFacade.master_track() is not None and SongFacade.master_track().muted

        return {
            "id": self._id,
            "active": self.active,
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
            seq.add(partial(Backend.client().notify_set_state, data))

            if self._title is None:
                seq.wait_for_backend_response()
                seq.add(lambda: setattr(self, "_title", seq.res["title"]))  # type: ignore[index]

            seq.done()

        self._cache = data

    def _disconnect(self):
        # type: () -> None
        Backend.client().close_set(self._id)
