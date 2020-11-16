import traceback
from threading import Timer
from typing import TYPE_CHECKING, Any

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.utils.log import log

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


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


def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                log("cancelling timer")
                debounced.t.cancel()
            except AttributeError:
                pass
            log("setting timer")
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator