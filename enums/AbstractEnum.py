from enum import Enum
from typing import TypeVar, cast, Optional

T = TypeVar("T", bound=Enum)


class AbstractEnum(Enum):
    def __str__(self):
        # type: () -> str
        return self.value

    @classmethod
    def get_from_value(cls, value, default=None):
        # type: (Optional[str], Optional[T]) -> Optional[T]
        if value is None:
            return default

        value = value.strip()
        for _, enum in cls.__members__.items():
            if value == enum.name:
                return cast(T, enum)

        return cast(T, default)
