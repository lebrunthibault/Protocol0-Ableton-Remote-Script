from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional

import Live
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.TrackColorEnum import TrackColorEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrackNameUpdatedEvent import (
    AbstractTrackNameUpdatedEvent,
)
from protocol0.domain.shared.decorators import defer
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.observer.Observable import Observable


class AbstractTrackAppearance(SlotManager, Observable):
    def __init__(self, live_track):
        # type: (Live.Track.Track) -> None
        super(AbstractTrackAppearance, self).__init__()
        self._live_track = live_track
        self._default_color = self.color
        self._instrument = None  # type: Optional[InstrumentInterface]
        self._name_listener.subject = live_track

    def set_instrument(self, instrument):
        # type: (Optional[InstrumentInterface]) -> None
        self._instrument = instrument

    @subject_slot("name")
    @defer
    def _name_listener(self):
        # type: () -> None
        if len(self.name) > 2:
            # .title is not good because of words starting with numbers
            self.name = " ".join([word.capitalize() for word in self.name.split(" ")])

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
            self._default_color = color_index
            self._live_track.color_index = color_index

    @property
    def computed_color(self):
        # type: () -> int
        return self._default_color

    def refresh(self):
        # type: () -> None
        if self._live_track.group_track and self._live_track.group_track.color_index != self._default_color:
            self._default_color = self._live_track.group_track.color_index

        self.color = self._default_color
        self.notify_observers()
