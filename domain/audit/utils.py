from typing import Callable, Any

from protocol0.domain.shared.backend.Backend import Backend


def tail_logs(func):
    # type: (Callable) -> Callable
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        res = func(*a, **k)

        Backend.client().tail_logs()

        return res

    return decorate
