import traceback
from typing import TYPE_CHECKING, Any

from a_protocol_0.utils.log import log

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


def action_decorator(unarm_other_tracks=False):
    def wrap(func):
        def decorate(self, *args, **kwargs):
            # type: ("Protocol0Component", Any, Any) -> None
            if not args[0]:
                return
            try:
                self.log_message("Executing " + func.__name__)
                func(self, *args, **kwargs)
            except Exception:
                self.log_message(traceback.format_exc())
                return

            if unarm_other_tracks:
                self.mySong().unarm_other_tracks()

        return decorate
    return wrap


def unarm_other_tracks(func):
    """ second decorator called (inner) """

    def decorate(self, *args, **kwargs):
        # type: ("Protocol0Component", Any, Any) -> None
        try:
            func(self, *args, **kwargs)
            self.mySong().unarm_other_tracks()
        except Exception as e: raise

    return decorate

def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:  # there's probably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate
