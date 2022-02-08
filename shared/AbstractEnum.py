from enum import Enum
from typing import TypeVar, cast, Any, Dict

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error

T = TypeVar("T", bound=Enum)


class AbstractEnum(Enum):
    def __str__(self):
        # type: () -> str
        return self.name

    @classmethod
    def from_value(cls, value):
        # type: (Any) -> T
        for _, enum in cls.__members__.items():
            if value == enum.value:
                return cast(T, enum)

        raise Protocol0Error("Couldn't find matching enum for value %s" % value)

    def get_value_from_mapping(self, mapping):
        # type: (Dict[AbstractEnum, Any]) -> Any
        if self not in mapping:
            raise Protocol0Error("Couldn't find enum %s in mapping" % self)
        return mapping[self]
