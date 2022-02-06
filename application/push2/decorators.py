from functools import wraps

from typing import TYPE_CHECKING, Any, Callable

from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.my_types import Func

if TYPE_CHECKING:
    from protocol0.application.push2.Push2Manager import Push2Manager


def push2_method(defer_call=True):
    # type: (bool) -> Callable
    def wrap(func):
        # type: (Func) -> Func
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (Push2Manager, Any, Any) -> Any
            # check hasattr in case the push2 is turned off during a set
            if not self.push2 or not hasattr(self.push2, "_initialized") or not self.push2._initialized:
                return

            def execute():
                # type: () -> Any
                with self.push2.component_guard():
                    return func(self, *a, **k)

            if defer_call:
                Scheduler.defer(execute)
            else:
                return execute()

        return decorate

    return wrap
