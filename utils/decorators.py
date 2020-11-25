import traceback
from typing import TYPE_CHECKING, Any

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.utils.log import log

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Pro import Protocol0Component
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


def arm_exclusive(auto_arm=False):
    def wrap(func):
        def decorate(self, *args, **kwargs):
            # type: ("AbstractTrack", Any, Any) -> None
            if auto_arm and self.can_be_armed and not self.arm:
                self.action_arm()
            func(self, *args, **kwargs)
            if self.arm:
                self.song.unarm_other_tracks()

        return decorate

    return wrap


def only_if_current(func):
    def decorate(self, *args, **kwargs):
        # type: ("AbstractTrack", Any, Any) -> None
        if self.song.current_track != self:
            return
        func(self, *args, **kwargs)

    return decorate


def button_action(unarm_other_tracks=False, is_scrollable=False):
    def wrap(func):
        @subject_slot("value")
        def decorate(self, *args, **kwargs):
            # type: ("Protocol0ComponentMixin", Any, Any) -> None
            value = args[0]
            if not value:
                return
            if is_scrollable:
                kwargs = dict(kwargs, go_next=value == 1)
            try:
                self.log_message("Executing " + func.__name__)
                func(self, **kwargs)
            except Exception:
                self.log_message(traceback.format_exc())
                return

            if unarm_other_tracks:
                self.my_song().unarm_other_tracks()

        return decorate

    return wrap


def print_except_decorator(func):
    def decorator(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            log(traceback.format_exc())
            return

    return decorator
