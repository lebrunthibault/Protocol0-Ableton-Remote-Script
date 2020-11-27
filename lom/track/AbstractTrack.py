from abc import ABCMeta, abstractproperty

from typing import Any, Optional
from typing import TYPE_CHECKING

from a_protocol_0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin
from a_protocol_0.consts import RECORDING_TIMES
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.ClipSlot import ClipSlot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyDeprecation
class AbstractTrack(AbstractTrackActionMixin, AbstractObject):
    __metaclass__ = ABCMeta

    def __init__(self, song, track, index):
        # type: ("Song", Any, int) -> None
        self._track = track  # type: Any
        self._index = index  # type: int
        self.song = song  # type: Song
        self.original_name = self.name
        self.recording_time = "1 bar"
        self.bar_count = 1
        self.recording_times = RECORDING_TIMES
        self.instrument = None  # type: Optional[AbstractInstrument]

    def __eq__(self, other):
        if isinstance(other, AbstractTrack):
            return self.track == other.track
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
    def index(self):
        # type: () -> int
        pass

    @abstractproperty
    def is_simple_group(self):
        # type: () -> bool
        pass

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
    def selectable_track(self):
        # type: () -> "SimpleTrack"
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
