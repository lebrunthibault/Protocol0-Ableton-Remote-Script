import glob
from functools import partial
from os.path import dirname, basename
from uuid import uuid4

from typing import Dict, Any, Optional, List

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
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AbletonSet(object):
    def __init__(self):
        # type: () -> None
        self._cache = {}  # type: Dict[str, Any]

        self._path = None  # type: Optional[str]
        self._title = None  # type: Optional[str]
        self._id = str(uuid4())
        self.active = True

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

        listened_events = [
            AbstractTrackNameUpdatedEvent,
            DrumRackLoadedEvent,
            MasterTrackRoomEqToggledEvent,
            MasterTrackMuteToggledEvent,
            SimpleTrackFirstClipAddedEvent,
            SimpleTrackLastClipDeletedEvent,
            TracksMappedEvent,
            SelectedTrackChangedEvent,
        ]

        for event in listened_events:
            DomainEventBus.subscribe(event, lambda _: self.notify())

    def __repr__(self):
        # type: () -> str
        return "AbletonSet(%s)" % self._title

    @property
    def is_unknown(self):
        # type: () -> bool
        return self._path is None

    @property
    def _saved_tracks(self):
        # type: () -> List[str]
        assert self._path, "set path not set"
        tracks_folder = "%s\\tracks" % dirname(self._path)

        filenames = glob.glob("%s\\*.als" % tracks_folder)

        return [basename(t).replace(".als", "") for t in filenames]

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
            "path": self._path,
            "title": self._title,
            "muted": muted,
            "current_track_name": SongFacade.current_track().name,
            "current_track_is_grouped": SongFacade.current_track().group_track is not None,
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
                seq.wait_for_backend_event("set_updated")
                seq.add(lambda: self._set_from_server_response(seq.res))  # type: ignore[arg-type]

            seq.done()

        self._cache = data

    def _set_from_server_response(self, res):
        # type: (Dict) -> None
        if self._title is not None:
            Logger.warning("Tried overwriting set title of %s" % self)
            return

        self._title = res["title"]
        self._path = res["path"]

        if not self.is_unknown:
            abstract_track_names = [t.name for t in SongFacade.abstract_tracks()]
            orphan_tracks = [t for t in self._saved_tracks if t not in abstract_track_names]

            if len(orphan_tracks):
                Backend.client().show_warning("Found orphan saved tracks: \n\n%s" % "\n".join(orphan_tracks))
                Backend.client().show_sub_tracks()

    def _disconnect(self):
        # type: () -> None
        Backend.client().close_set(self._id)
