from pydoc import classname, locate

from enum import Enum
from typing import TypeVar, cast, Optional

T = TypeVar("T", bound=Enum)


class AbstractEnum(Enum):
    def __str__(self):
        # type: () -> str
        return self.name

    def is_json_enum(self, json_value):
        # type: (str) -> bool
        return isinstance(json_value, dict) and json_value.get("type") == "Enum"

    def to_json_dict(self):
        # type: () -> dict
        return {
            "type": "Enum",
            "classname": classname(self.__class__, ""),
            "name": self.name
        }

    @classmethod
    def from_json_dict(cls, json_dict):
        # type: (dict) -> AbstractEnum
        sub_class = locate(json_dict["classname"])
        return getattr(sub_class, json_dict["name"])

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
