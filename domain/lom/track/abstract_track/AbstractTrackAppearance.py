import Live
from typing import Optional

from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.TrackColorEnum import TrackColorEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrackNameUpdatedEvent import AbstractTrackNameUpdatedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class AbstractTrackAppearance(object):
    def __init__(self, live_track):
        # type: (Live.Track.Track) -> None
        self._live_track = live_track
        self._default_color = self.color
        self._instrument = None  # type: Optional[InstrumentInterface]

    def set_instrument(self, instrument):
        # type: (InstrumentInterface) -> None
        self._instrument = instrument

    @property
    def name(self):
        # type: () -> str
        return self._live_track.name if self._live_track else ""

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._live_track and name:
            self._live_track.name = str(name).strip()
            DomainEventBus.emit(AbstractTrackNameUpdatedEvent())

    @property
    def color(self):
        # type: () -> int
        if self._live_track:
            return self._live_track.color_index
        else:
            return TrackColorEnum.DISABLED.color_int_value

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        if self._live_track and color_index != self._live_track.color_index:
            self._live_track.color_index = color_index

    @property
    def computed_color(self):
        # type: () -> int
        return self._default_color
