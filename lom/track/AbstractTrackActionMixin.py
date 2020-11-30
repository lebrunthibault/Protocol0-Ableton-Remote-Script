from abc import abstractmethod
from typing import TYPE_CHECKING, Callable

from a_protocol_0.utils.decorators import arm_exclusive, only_if_current

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin(object):
    @arm_exclusive()
    @only_if_current
    def action_arm(self):
        # type: ("AbstractTrack") -> None
        self.action_arm_track() if not self.arm and self.can_be_armed else None

    @abstractmethod
    def action_arm_track(self):
        # type: ("AbstractTrack") -> None
        pass

    @abstractmethod
    def action_unarm(self):
        # type: ("AbstractTrack") -> None
        pass

    @only_if_current
    def action_sel(self):
        # type: ("AbstractTrack") -> None
        if self.is_simple_group:
            return
        self.parent.application().view.show_view(u'Detail/DeviceChain')
        self.selectable_track.is_selected = True
        self.is_folded = False
        if self.instrument.can_be_shown:
            self.instrument.show()

    @abstractmethod
    def switch_monitoring(self):
        # type: ("AbstractTrack") -> None
        pass

    @arm_exclusive(auto_arm=True)
    def action_restart_and_record(self, action_record_func, only_audio=False):
        # type: ("AbstractTrack", Callable, bool) -> None
        """ restart audio to get a count in and recfix"""
        if self.is_recording:
            return self.action_undo()

        self.song.is_playing = False
        action_record_func()

        if len(self.song.playing_tracks) <= 1 and not only_audio:
            self.song.metronome = True
            self.parent.wait_bars(self.bar_count + 1, self.action_post_record)

    def action_post_record(self):
        # type: ("AbstractTrack") -> None
        self.song.metronome = False

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

    @abstractmethod
    def stop(self):
        # type: ("AbstractTrack") -> None
        pass

    def action_undo(self):
        # type: ("AbstractTrack") -> None
        self.parent.clear_tasks()
        self.action_undo_track()

    @abstractmethod
    def action_undo_track(self):
        # type: ("AbstractTrack") -> None
        pass
