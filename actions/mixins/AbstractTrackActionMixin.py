from abc import abstractmethod, abstractproperty

from typing import Optional, TYPE_CHECKING, Callable

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
        return self.record_track.action_set_monitor_in(not self.record_track.has_monitor_in)

    def action_restart_and_record(self, action_record_func):
        # type: ("AbstractTrack", Callable, Optional[int]) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"
        action_list += self.action_arm
        action_list += self.record_track.action_add_scene_if_needed
        action_list += self.action_stop

        if not self.song.has_set_playing_clips(self):
            action_list += "; metro on"

        action_list += action_record_func()
        action_list += "; wait {0}; metro off; wait 2".format(self.song.delay_before_recording_end(self.bar_count))

        if self.record_track.is_audio:
            action_list += "; {0}/clip({1}) warpmode complex".format(self.record_track.index, self.rec_clip_index)
        if self.is_group_track:
            action_list += self.action_set_audio_playing_color(Colors.PLAYING)
            if self.song.current_action_name == "record_ext":
                action_list += self.record_track.action_set_monitor_in()

        action_list += self.action_rename_recording_clip

        return action_list

    @abstractmethod
    def action_record_all(self):
        # type: () -> str
        """ this records normally on a simple track and both midi and audio on a group track """
        pass

    @abstractmethod
    def action_record_audio_only(self):
        # type: ("AbstractTrack") -> str
        """
            this records normally on a simple track and only audio on a group track
            is is available on simple tracks just for ease of use
        """
        pass

    @abstractproperty
    def action_rename_recording_clip(self):
        # type: ("AbstractTrack") -> str
        pass

    @abstractproperty
    def action_stop(self):
        # type: ("AbstractTrack") -> str
        pass

    @abstractproperty
    def action_undo(self):
        # type: ("AbstractTrack") -> str
        pass
