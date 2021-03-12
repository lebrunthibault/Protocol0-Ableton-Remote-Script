from enum import Enum


class AbstractEnum(Enum):
    @classmethod
    def default(cls):
        raise NotImplementedError

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def get_from_value(cls, value):
        value = value.strip()
        if not value or not cls.has_value(value):
            return cls.default()
        else:
            return cls(value)
