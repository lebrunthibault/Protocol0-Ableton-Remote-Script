from abc import abstractmethod, abstractproperty

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin:
    @abstractproperty
    def action_arm(self):
        # type: ("AbstractTrack") -> str
        pass

    @abstractmethod
    def action_unarm(self, direct_unarm):
        # type: ("AbstractTrack", bool) -> str
        pass

    @abstractproperty
    def action_sel(self):
        # type: ("AbstractTrack") -> str
        pass

    def action_start_or_stop(self):
        # type: ("AbstractTrack") -> str
        if self.record_track.is_foldable:
            return ""
        self.record_track.set_monitor_in(not self.record_track.has_monitor_in)
        return ""

    @abstractproperty
    def action_restart(self):
        # type: ("AbstractTrack") -> str
        pass

    def action_record_track(self, bar_count=128):
        # type: ("AbstractTrack", Optional[int]) -> str
        action_list = self.action_arm
        action_list += self.record_track.action_add_scene_if_needed
        action_list += self.action_record(bar_count)

        return action_list

    @abstractmethod
    def action_record(self, bar_count):
        # type: (Optional[int]) -> str
        pass

    @abstractproperty
    def action_record_audio(self):
        # type: ("AbstractTrack") -> str
        pass

    @abstractproperty
    def action_undo(self):
        # type: ("AbstractTrack") -> str
        pass
