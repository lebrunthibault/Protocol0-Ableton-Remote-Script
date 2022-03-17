from typing import Dict

from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade


class SongState(object):
    def __init__(self):
        # type: () -> None
        DomainEventBus.subscribe(TracksMappedEvent, lambda _: self.notify())

    def to_dict(self):
        # type: () -> Dict
        return {
            "track_names": [track.name for track in SongFacade.simple_tracks()]
        }

    def notify(self):
        # type: () -> None
        Backend.client().notify_song_state(self.to_dict())
