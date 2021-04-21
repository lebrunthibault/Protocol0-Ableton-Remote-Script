from enum import Enum
from typing import NoReturn, TypeVar, cast

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
    def get_from_value(cls, value):
        # type: (str) -> T
        value = value.strip()
        for int, enum in cls.__members__.items():
            if value == enum.value:
                return cast(T, enum)

        return cls.default()
