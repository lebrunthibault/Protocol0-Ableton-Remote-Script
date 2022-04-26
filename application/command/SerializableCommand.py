import json
from pydoc import classname, locate

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class SerializableCommand(object):
    def __repr__(self):
        # type: () -> str
        return self.serialize()

    def serialize(self):
        # type: () -> str
        """Used from outside"""
        return json.dumps({
            "class": classname(self.__class__, ""),
            "args": self.__dict__
        }, sort_keys=True, indent=4)

    @classmethod
    def unserialize(cls, json_string):
        # type: (str) -> SerializableCommand
        json_dict = json.loads(json_string)
        assert "class" in json_dict, "class is missing from json serialization"
        assert "args" in json_dict, "attrs is missing from json serialization"

        sub_class = locate(json_dict["class"])
        if not sub_class:
            raise Protocol0Error("Couldn't locate %s" % json_dict["class"])

        # noinspection PyCallingNonCallable
        return sub_class(**json_dict["args"])  # type: ignore[operator]
