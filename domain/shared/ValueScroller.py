from typing import List, Generic

from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.types import T


class ValueScroller(Generic[T]):
    def __init__(self, initial_value):
        # type: (T) -> None
        self._current_value = initial_value

    def __str__(self):
        # type: () -> str
        return self.__class__.__name__

    @property
    def current_value(self):
        # type: () -> T
        return self._current_value

    def scroll(self, go_next):
        # type: (bool) -> None
        self._current_value = scroll_values(self._get_values(), self._get_initial_value(go_next), go_next=go_next)
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
