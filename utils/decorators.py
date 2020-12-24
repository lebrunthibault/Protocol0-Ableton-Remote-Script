import traceback
from functools import partial, wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
    # noinspection PyUnresolvedReferences
    from a_protocol_0.components.Push2Manager import Push2Manager


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def push2_method(defer=True):
    def wrap(func):
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (Push2Manager) -> None
            # check hasattr in case the push2 is turned off during a set
            if not self.push2 or not hasattr(self.push2, "_initialized") or not self.push2._initialized:
                return

            def execute():
                with self.push2.component_guard():
                    func(self, *a, **k)

            if defer:
                self.parent.defer(execute)
            else:
                execute()

        return decorate

    return wrap


def defer(func):
    @wraps(func)
    def decorate(self, *a, **k):
        # type: (AbstractControlSurfaceComponent) -> None
        self.parent.defer(partial(func, self, *a, **k))

    return decorate


def debounce(func):
    @wraps(func)
    def decorate(self, *a, **k):
        # type: (AbstractControlSurfaceComponent) -> None
        decorate.count += 1
        self.parent._wait(3, partial(execute, func, self, *a, **k))

    decorate.count = 0

    def execute(func, *a, **k):
        decorate.count -= 1
        if decorate.count == 0:
            func(*a, **k)

    return decorate


def button_action(auto_arm=False, log_action=True):
    def wrap(func):
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (AbstractControlSurfaceComponent) -> None
            if log_action:
                self.parent.log_info("Executing " + func.__name__)
            try:
                if auto_arm:
                    self.song.unfocus_all_tracks()
                    if not self.song.current_track.arm:
                        self.song.current_track.action_arm()
                func(self, **k)
            except Exception:
                self.parent.log_info(traceback.format_exc())
                return

        return decorate

    return wrap


def catch_and_log(func):
    @wraps(func)
    def decorate(self, *a, **k):
        # type: (AbstractControlSurfaceComponent) -> None
        try:
            func(self, *a, **k)
        except Exception:
            self.parent.log_info(traceback.format_exc())
            return

    return decorate


def disablable(func):
    """ allows one time disabling of a method """

    @wraps(func)
    def decorate(*a, **k):
        if not func.enabled:
            func.enabled = True
        else:
            func(*a, **k)

    return decorate
