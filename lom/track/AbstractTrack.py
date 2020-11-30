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
        self.g_track = None  # type: Optional[GroupTrack]
        self.recording_times = RECORDING_TIMES
        self.children = []  # type: list[AbstractTrack]
        self.recording_time = "1 bar"
        self.bar_count = 1
        self.instrument = AbstractInstrument.create_from_abstract_track(self)

    def __eq__(self, other):
        if isinstance(other, AbstractTrack):
            return self._track == other._track
        return False

    @property
    def index(self):
        # type: () -> int
        return self.base_track._index

    @property
    def base_track(self):
        # type: () -> SimpleTrack
        from a_protocol_0.lom.track.GroupTrack import GroupTrack
        return self.group if isinstance(self, GroupTrack) else self

    @property
    def selectable_track(self):
        # type: () -> SimpleTrack
        from a_protocol_0.lom.track.GroupTrack import GroupTrack
        return self.midi if isinstance(self, GroupTrack) else self

    @property
    def is_simple_group(self):
        # type: () -> bool
        return self.is_foldable and not self.is_group_ex_track

    @property
    def is_group_ex_track(self):
        # type: () -> bool
        from a_protocol_0.lom.track.GroupTrack import GroupTrack
        return isinstance(self, GroupTrack)

    @property
    def all_nested_children(self):
        # type: () -> list["SimpleTrack"]
        nested_children = []
        for child in self.children:
            nested_children.append(child)
            nested_children += child.all_nested_children
        return nested_children

    @property
    def name(self):
        # type: () -> str
        return self._track.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        self._track.name = name

    @property
    def is_foldable(self):
        # type: () -> bool
        return self.base_track._track.is_foldable

    @property
    def is_folded(self):
        # type: () -> bool
        return self._track.fold_state if self.is_foldable else False

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if self.is_foldable:
            self._track.fold_state = int(is_folded)

    @abstractproperty
    def is_playing(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_recording(self):
        # type: () -> bool
        pass

    @property
    def can_be_armed(self):
        # type: () -> bool
        return self.selectable_track._track.can_be_armed

    @abstractproperty
    def arm(self):
        # type: () -> bool
        pass

    @abstractproperty
    def next_empty_clip_slot(self):
        # type: () -> ClipSlot
        pass
