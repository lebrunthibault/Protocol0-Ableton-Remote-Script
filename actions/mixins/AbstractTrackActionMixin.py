from abc import abstractmethod
from functools import partial

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin(object):
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
        # type: ("AbstractTrack") -> None
        pass

    def switch_monitoring(self):
        # type: ("AbstractTrack") -> None
        pass

    def action_restart_and_record(self, action_record_func):
        # type: ("AbstractTrack", Callable) -> None
        """ restart audio to get a count in and recfix"""
        self.song.is_playing = False
        self.stop()
        self.action_arm()

        if self.is_recording:
            self.action_undo()

        self.song.metronome = len(self.song.playing_tracks) > 1

        action_record_func()
        self.parent.wait_bars(self.bar_count, partial(self.action_post_record))

    @abstractmethod
    def action_record_all(self):
        # type: () -> None
        """ this records normally on a simple track and both midi and audio on a group track """
        pass

    @abstractmethod
    def action_post_record(self):
        # type: ("AbstractTrack") -> None
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

    @abstractmethod
    def action_undo(self):
        # type: ("AbstractTrack") -> None
        pass
