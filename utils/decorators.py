import traceback
from functools import partial
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
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
        def decorate(self, *a, **k):
            # type: (Push2Manager, Any, Any) -> None
            if not self.push2 or not self.push2._initialized:
                return

            def execute():
                with self.push2.component_guard():
                    func(self, *a, **k)

            if defer:
                self.parent.defer(execute)
            else:
                execute

        return decorate

    return wrap


def augment(func, func2):
    def decorate(*a, **k):
        func(*a, **k)
        func2()

    return decorate


def defer(func):
    def decorate(self, *a, **k):
        # type: (AbstractControlSurfaceComponent, Any, Any) -> None
        self.parent.defer(partial(func, self, *a, **k))

    return decorate


def button_action(auto_arm=False, log_action=True):
    def wrap(func):
        def decorate(self, *a, **k):
            # type: (AbstractControlSurfaceComponent, Any, Any) -> None
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
