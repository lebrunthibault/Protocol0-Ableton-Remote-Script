from enum import Enum
from typing import TypeVar, cast

T = TypeVar("T", bound=Enum)


class AbstractEnum(Enum):
    @classmethod
    def default(cls):
        # type: (T) -> T
        raise NotImplementedError

    @classmethod
    def get_from_value(cls, value):
        # type: (str) -> T
        value = value.strip()
        for int, enum in cls.__members__.items():
            if value == enum.value:
                return cast(T, enum)

        return cast(T, cls.default())
