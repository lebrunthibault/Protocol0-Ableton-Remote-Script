import inspect

from a_protocol_0.components.SearchManager import SearchManager
from a_protocol_0.enums.AbstractEnum import AbstractEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error


class ServerActionEnum(AbstractEnum):
    def __eq__(self, string):
        # type: (str) -> bool
        return self.name == string

    def get_method_name(self):
        # type: () -> str
        if "method" not in self.value or not inspect.ismethod(self.value["method"]):
            raise Protocol0Error("Invalid enum value %s" % self)

        return self.value["method"].__name__

    SEARCH_TRACK = {"method": SearchManager.search_track}
