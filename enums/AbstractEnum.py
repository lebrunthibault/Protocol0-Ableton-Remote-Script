from enum import Enum
from typing import List, NoReturn, TypeVar

T = TypeVar("T", bound=Enum)


class AbstractEnum(Enum):
    @classmethod
    def default(cls):
        # type: () -> NoReturn
        raise NotImplementedError

    @classmethod
    def has_key(cls, key):
        # type: (str) -> bool
        return hasattr(cls, key)

    @classmethod
    def values(cls):
        # type: () -> List[T]
        return cls._value2member_map_.values()

    @classmethod
    def get_from_value(cls, value):
        # type: (str) -> T
        value = value.strip()
        for int, enum in cls._value2member_map_:
            if value == enum.value:
                return enum

        return cls.default()
