from typing import Generic
from typing import Optional, List, Iterable

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils.utils import clamp
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.types import T


class ValueScroller(Generic[T]):
    def __init__(self, initial_value):
        # type: (T) -> None
        self._current_value = initial_value

    def __str__(self):
        # type: () -> str
        return self.__class__.__name__

    @classmethod
    def scroll_values(cls, items, current_value, go_next, rotate=True):
        # type: (Iterable[T], Optional[T], bool, bool) -> T
        values = list(items)  # type: List[T]
        if len(values) == 0:
            raise Protocol0Warning("empty list handed to scroll_values")

        if current_value not in values:
            # find the neighbor
            if current_value is not None and hasattr(current_value, "index"):
                values.append(current_value)
                values.sort(key=lambda x: x.index)  # type: ignore[attr-defined]
            else:
                return values[0]

        increment = 1 if go_next else -1
        current_index = values.index(current_value)
        next_index = current_index + increment

        if rotate is False:
            next_index = int(clamp(next_index, 0, len(values) - 1))
        else:
            next_index = (current_index + increment) % len(values)

        return values[next_index]

    @property
    def current_value(self):
        # type: () -> T
        return self._current_value

    def scroll(self, go_next):
        # type: (bool) -> None
        self._current_value = self.scroll_values(
            self._get_values(), self._get_initial_value(go_next), go_next=go_next
        )
        self._value_scrolled()

    def _get_initial_value(self, go_next):
        # type: (bool) -> T
        return self._current_value

    def _get_values(self):
        # type: () -> List[T]
        raise NotImplementedError

    def _value_scrolled(self):
        # type: () -> None
        StatusBar.show_message("%s : %s" % (self, self.current_value))
