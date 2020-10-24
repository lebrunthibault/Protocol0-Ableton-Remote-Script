from abc import abstractmethod, abstractproperty

from typing import Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors

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

    def action_restart_and_record(self, action_record_func, bar_count=128):
        # type: ("AbstractTrack", int) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"
        action_list += self.action_arm
        action_list += self.record_track.action_add_scene_if_needed

        if not self.song.has_set_playing_clips(self) and self.activate_metro:
            action_list += "; metro on"

        action_list += self.action_record_all(bar_count)
        action_list += "; wait {0}; metro off;".format(self.song.delay_before_recording_end(bar_count))

        if self.record_track.is_audio:
            action_list += "; {0}/clip({1}) warpmode complex".format(self.record_track.index, self.rec_clip_index)
        if self.is_group_track:
            action_list += self.action_set_audio_playing_color(Colors.PLAYING)

        return action_list

    @abstractmethod
    def action_record_all(self, bar_count):
        # type: (Optional[int]) -> str
        """ this records normally on a simple track and both midi and audio on a group track """
        pass

    @abstractproperty
    def action_record_audio_only(self):
        # type: ("AbstractTrack") -> str
        """
            this records normally on a simple track and only audio on a group track
            is is available on simple tracks just for ease of use
        """
        pass

    @abstractproperty
    def action_undo(self):
        # type: ("AbstractTrack") -> str
        pass
