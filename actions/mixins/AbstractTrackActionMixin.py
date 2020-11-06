from abc import abstractmethod, abstractproperty

from typing import Optional, TYPE_CHECKING, Callable

from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin:
    @abstractmethod
    def action_arm(self):
        # type: ("AbstractTrack") -> None
        pass

    @abstractmethod
    def action_unarm(self, direct_unarm):
        # type: ("AbstractTrack", bool) -> None
        pass

    @abstractmethod
    def action_sel(self):
        # type: ("AbstractTrack") -> Optional[str]
        pass

    def action_switch_monitoring(self):
        # type: ("AbstractTrack") -> None
        pass

    def action_restart_and_record(self, action_record_func):
        # type: ("AbstractTrack", Callable, Optional[int]) -> str
        """ restart audio to get a count in and recfix"""
        self.song.is_playing = False
        self.action_arm()
        self.record_track.action_add_scene_if_needed()
        self.stop_all_clips()

        if not self.song.has_set_playing_clips(self):
            self.song.metronome = True

        action_record_func()
        action_list = "; wait {0}; metro off; wait 2".format(self.song.delay_before_recording_end(self.bar_count))

        if self.record_track.is_audio:
            action_list += "; {0}/clip({1}) warpmode complex".format(self.record_track.index, self.rec_clip_index)
        from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
        if isinstance(self, GroupTrack):
            list(self.clyphx.clips.values())[1].color = Colors.PLAYING
            if self.song.current_action_name == "record_ext":
                self.record_track.has_monitor_in = True

        action_list += self.action_rename_recording_clip

        return action_list

    @abstractmethod
    def action_record_all(self):
        # type: () -> None
        """ this records normally on a simple track and both midi and audio on a group track """
        pass

    @abstractmethod
    def action_record_audio_only(self):
        # type: ("AbstractTrack") -> None
        """
            this records normally on a simple track and only audio on a group track
            is is available on simple tracks just for ease of use
        """
        pass

    @abstractproperty
    def action_rename_recording_clip(self):
        # type: ("AbstractTrack") -> str
        pass

    @abstractmethod
    def stop_all_clips(self):
        # type: ("AbstractTrack") -> None
        pass

    @abstractproperty
    def action_undo(self):
        # type: ("AbstractTrack") -> str
        pass
