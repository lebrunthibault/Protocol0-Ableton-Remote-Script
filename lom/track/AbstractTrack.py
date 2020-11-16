from abc import ABCMeta, abstractproperty

from typing import Any
from typing import TYPE_CHECKING

from a_protocol_0.actions.mixins.AbstractTrackActionMixin import AbstractTrackActionMixin
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.ClipSlot import ClipSlot

if TYPE_CHECKING:
    from a_protocol_0.lom.Song import Song
    from a_protocol_0.Protocol0Component import Protocol0Component


# noinspection PyDeprecation
class AbstractTrack(AbstractTrackActionMixin):
    __metaclass__ = ABCMeta

    def __init__(self, song, track, index):
        # type: ("Song", Any, int) -> None
        self._track = track  # type: Any
        self._index = index  # type: int
        self.song = song  # type: Song
        self.original_name = self.name

    def __eq__(self, other):
        if isinstance(other, AbstractTrack):
            return self.index == other.index
        return False

    @property
    def parent(self):
        # type: () -> Protocol0Component
        return self.song.parent

    @abstractproperty
    def track(self):
        # type: () -> Any
        pass

    @property
    def name(self):
        # type: () -> str
        return self.track.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        self.track.name = name

    @abstractproperty
    def instrument(self):
        # type: () -> AbstractInstrument
        pass

    @abstractproperty
    def index(self):
        # type: () -> int
        pass

    @property
    def bar_count(self):
        # type: () -> int
        return self.song.bar_count

    @abstractproperty
    def is_foldable(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_folded(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_playing(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_recording(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_visible(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_top_visible(self):
        # type: () -> bool
        pass

    @abstractproperty
    def can_be_armed(self):
        # type: () -> bool
        pass

    @abstractproperty
    def arm(self):
        # type: () -> bool
        pass

    @abstractproperty
    def next_empty_clip_slot(self):
        # type: () -> ClipSlot
        pass
