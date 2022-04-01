from typing import Optional, Generic

from protocol0.shared.types import T


class ValueToggler(Generic[T]):
    def __init__(self, value=None):
        # type: (Optional[T]) -> None
        self._value = value

    @property
    def value(self):
        # type: () -> Optional[T]
        return self._value

    def toggle(self):
        # type: () -> None
        old_value = self._value
        new_value = self._get_value()
        if old_value == new_value:
            self._value = None
        else:
            self._value = new_value
            self._value_set(new_value)

        if old_value:
            self._value_unset(old_value)

    def reset(self):
        # type: () -> None
        self._value = None

    def _value_set(self, value):
        # type: (T) -> None
        pass

    def _value_unset(self, value):
        # type: (T) -> None
        pass

    def _get_value(self):
        # type: () -> T
        raise NotImplementedError
