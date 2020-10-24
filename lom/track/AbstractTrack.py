from typing import Any, Optional
from abc import ABCMeta, abstractproperty, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


# noinspection PyDeprecation
class AbstractTrack(object):
    __metaclass__ = ABCMeta

    def __init__(self, song, track, index):
        # type: (Any, Any, int) -> None
        self._track = track
        self._index = index
        self.song = song

    def __eq__(self, other):
        if isinstance(other, AbstractTrack):
            return self.index == other.index
        return False

    #### ACTIONS ####

    @abstractmethod
    def action_arm(self):
        # type: () -> str
        pass

    @abstractmethod
    def action_unarm(self, direct_unarm):
        # type: (Optional[bool]) -> str
        pass

    @abstractmethod
    def action_sel(self):
        # type: () -> str
        pass

    @abstractmethod
    def action_show(self):
        # type: () -> str
        pass

    def action_start_or_stop(self):
        # type: () -> str
        if self.record_track.is_foldable:
            return ""
        self.record_track.set_monitor_in(not self.record_track.has_monitor_in)
        return ""

    @abstractmethod
    def action_record(self, bar_count):
        # type: (Optional[int]) -> str
        pass

    @abstractmethod
    def action_record_audio(self):
        # type: () -> str
        pass

    @abstractmethod
    def action_undo(self):
        # type: () -> str
        pass

    @abstractmethod
    def action_scroll_preset_or_sample(self, go_next):
        # type: (bool) -> str
        pass

    @abstractproperty
    def track(self):
        # type: () -> Any
        pass

    @abstractproperty
    def index(self):
        # type: () -> int
        pass

    @abstractproperty
    def name(self):
        # type: () -> str
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
