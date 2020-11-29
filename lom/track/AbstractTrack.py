from abc import ABCMeta, abstractproperty
from typing import Any, Optional
from typing import TYPE_CHECKING

from a_protocol_0.consts import RECORDING_TIMES
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrackActionMixin import AbstractTrackActionMixin

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.GroupTrack import GroupTrack


# noinspection PyDeprecation
class AbstractTrack(AbstractTrackActionMixin, AbstractObject):
    __metaclass__ = ABCMeta

    def __init__(self, track, index, *a, **k):
        # type: (Any, int, Any, Any) -> None
        super(AbstractTrack, self).__init__(*a, **k)
        self._track = track  # type: Any
        self._index = index  # type: int
        self.g_track = None  # type: Optional["GroupTrack"]
        self.recording_times = RECORDING_TIMES
        self.recording_time = "1 bar"
        self.bar_count = 1
        self.instrument = AbstractInstrument.create_from_abstract_track(self)

    def __eq__(self, other):
        if isinstance(other, AbstractTrack):
            return self.track == other.track
        return False

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

    @property
    def is_folded(self):
        # type: () -> bool
        return self.track.fold_state if self.is_foldable else False

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if self.is_foldable:
            self.track.fold_state = int(is_folded)

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
