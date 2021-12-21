from pydoc import classname, locate

from enum import Enum
from typing import TypeVar, cast, Optional, Any, Dict

from protocol0.errors.Protocol0Error import Protocol0Error

T = TypeVar("T", bound=Enum)


class AbstractEnum(Enum):
    def __str__(self):
        # type: () -> str
        return self.name

    @classmethod
    def is_json_enum(cls, json_value):
        # type: (Any) -> bool
        return isinstance(json_value, dict) and json_value.get("type") == "Enum"

    def to_json(self):
        # type: () -> dict
        return {
            "type": "Enum",
            "classname": classname(self.__class__, ""),
            "name": self.name
        }

    @classmethod
    def from_json_dict(cls, json_dict):
        # type: (dict) -> Optional[AbstractEnum]
        sub_class = locate(json_dict["classname"])
        if not sub_class:
            raise Protocol0Error("Couldn't locate %s" % json_dict["classname"])
        return getattr(sub_class, json_dict["name"])

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
