import time
import traceback
from threading import Timer
from typing import TYPE_CHECKING, Any

from _Framework.SubjectSlot import subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


def arm_exclusive(func):
    def decorate(self, *args, **kwargs):
        # type: ("AbstractTrack", Any, Any) -> None
        func(self, *args, **kwargs)
        if self.arm:
            self.song.unarm_other_tracks()

    return decorate


def only_if_current(func):
    def decorate(self, *args, **kwargs):
        # type: ("AbstractTrack", Any, Any) -> None
        if self.song.current_track != self:
            return
        func(self, *args, **kwargs)

    return decorate


def button_action(unarm_other_tracks=False, is_scrollable=False):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """

    def wrap(func):
        @subject_slot("value")
        def decorate(self, *args, **kwargs):
            # type: ("Protocol0Component", Any, Any) -> None
            value = args[0]
            if not value:
                return
            try:
                if is_scrollable:
                    kwargs = dict(kwargs, go_next=value == 1)
                self.log_message("Executing " + func.__name__)
                func(self, **kwargs)
            except Exception:
                self.log_message(traceback.format_exc())
                return

            if unarm_other_tracks:
                self.mySong().unarm_other_tracks()

        return decorate

    return wrap
