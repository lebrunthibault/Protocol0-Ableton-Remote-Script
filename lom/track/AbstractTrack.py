from abc import ABCMeta, abstractproperty

from typing import Any
from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.mixins.AbstractTrackActionMixin import AbstractTrackActionMixin
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
    from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


# noinspection PyDeprecation
class AbstractTrack(AbstractTrackActionMixin, object):
    __metaclass__ = ABCMeta

    def __init__(self, song, track, index):
        # type: (Any, Any, int) -> None
        self._track = track  # type: Any
        self._index = index  # type: int
        self.song = song  # type: Song
        self.name = TrackName(self)  # type: TrackName

    def __eq__(self, other):
        if isinstance(other, AbstractTrack):
            return self.index == other.index
        return False

    @abstractproperty
    def track(self):
        # type: () -> Any
        pass

    @abstractproperty
    def instrument(self):
        # type: () -> AbstractInstrument
        pass

    @abstractproperty
    def index(self):
        # type: () -> int
        pass

    @property
    def is_group_track(self):
        # type: () -> bool
        from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
        return isinstance(self, GroupTrack)

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
    def is_armed(self):
        # type: () -> bool
        pass

    @abstractproperty
    def has_empty_slot(self):
        # type: () -> bool
        pass

    @abstractproperty
    def scene_count(self):
        # type: () -> int
        pass

    @abstractproperty
    def first_empty_slot_index(self):
        # type: () -> int
        pass

    @abstractproperty
    def rec_clip_index(self):
        # type: () -> int
        pass

    @abstractproperty
    def record_track(self):
        # type: () -> SimpleTrack
        pass
