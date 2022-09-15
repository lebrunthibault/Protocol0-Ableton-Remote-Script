import inspect
from collections import defaultdict
from functools import wraps, partial

from typing import Any, Optional

from protocol0.shared.types import Func


def lock(func):
    # type: (Func) -> Func
    from protocol0.shared.sequence.Sequence import Sequence

    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> Optional[Sequence]
        object_source = a[0] if inspect.ismethod(func) else decorate
        if decorate.lock[object_source]:  # type: ignore[attr-defined]
            return None

        decorate.lock[object_source] = True  # type: ignore[attr-defined]

        def unlock():
            # type: ()  -> None
            decorate.lock[object_source] = False  # type: ignore[attr-defined]

        seq = Sequence()
        seq.add(partial(func, *a, **k))
        seq.add(unlock)
        return seq.done()

    decorate.lock = defaultdict(int)  # type: ignore[attr-defined]

    return decorate
