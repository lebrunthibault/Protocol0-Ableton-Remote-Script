from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin:
    @abstractmethod
    def action_arm(self):
        # type: ("AbstractTrack") -> str
        pass

    @abstractmethod
    def action_unarm(self, direct_unarm):
        # type: ("AbstractTrack", Optional[bool]) -> str
        pass

    @abstractmethod
    def action_sel(self):
        # type: ("AbstractTrack") -> str
        pass

    def action_start_or_stop(self):
        # type: ("AbstractTrack") -> str
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
        # type: ("AbstractTrack") -> str
        pass

    @abstractmethod
    def action_undo(self):
        # type: ("AbstractTrack") -> str
        pass

    @abstractmethod
    def action_scroll_preset_or_sample(self, go_next):
        # type: ("AbstractTrack", bool) -> str
        pass
