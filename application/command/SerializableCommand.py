import json
from pydoc import classname, locate

from typing import Optional

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class SerializableCommand(object):
    def __init__(self):
        # type: () -> None
        self.set_id = None  # type: Optional[str]

    def __repr__(self):
        # type: () -> str
        if len(self.__dict__) == 0:
            return self.__class__.__name__
        else:
            kwargs = ",".join(["%s=%s" % (k, v) for k, v in self.__dict__.items()])
            return "%s(%s)" % (self.__class__.__name__, kwargs)

    def serialize(self):
        # type: () -> str
        """Used from outside"""
        return json.dumps(
            {"class": classname(self.__class__, ""), "args": self.__dict__},
            sort_keys=True,
            indent=4,
        )

    @classmethod
    def un_serialize(cls, json_string):
        # type: (str) -> SerializableCommand
        json_dict = json.loads(json_string)
        assert "class" in json_dict, "class is missing from json serialization"
        assert "args" in json_dict, "attrs is missing from json serialization"

        sub_class = locate(json_dict["class"])
        if not sub_class:
            raise Protocol0Error("Couldn't locate %s" % json_dict["class"])

        args = json_dict["args"]

        set_id = args.get("set_id", None)
        if "set_id" in args:
            del args["set_id"]

        # noinspection PyCallingNonCallable
        command = sub_class(**args)  # type: ignore[operator]
        command.set_id = set_id

        return command
