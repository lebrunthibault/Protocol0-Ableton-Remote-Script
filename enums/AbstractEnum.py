from enum import Enum
from typing import List


class AbstractEnum(Enum):
    @classmethod
    def default(cls):
        raise NotImplementedError

    @classmethod
    def has_key(cls, key):
        # type: (str) -> bool
        return hasattr(cls, key)

    @classmethod
    def has_value(cls, value):
        # type: (AbstractEnum) -> bool
        return value in cls._value2member_map_

    @classmethod
    def values(cls):
        # type: () -> List[AbstractEnum]
        return cls._value2member_map_.values()

    @classmethod
    def get_from_value(cls, value):
        value = value.strip()
        if not value or not cls.has_value(value):
            return cls.default()
        else:
            return cls(value)
