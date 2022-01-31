from typing import Type, Any, Optional, TYPE_CHECKING

from protocol0.enums.AbstractEnum import AbstractEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.utils.log import log_ableton
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.routing.TrackInputRouting import TrackInputRouting


class RoutingDescriptor(object):
    def __init__(self, enum_class, routing_attribute_name):
        # type: (Type[AbstractEnum], str) -> None
        self.enum_class = enum_class
        self.routing_attribute_name = routing_attribute_name
        self.available_routings_attribute_name = "available_%ss" % routing_attribute_name

    def __get__(self, track, objtype):
        # type: (TrackInputRouting, Type) -> Optional[Any]
        log_ableton("getting from %s and %s / %s" % (track._track, self.routing_attribute_name, self.available_routings_attribute_name))
        log_ableton(getattr(track._track, self.routing_attribute_name).display_name)
        log_ableton(list(self.enum_class))
        try:
            return self.enum_class.from_value(getattr(track._track, self.routing_attribute_name).display_name)
        except Protocol0Error:
            return None

    def __set__(self, track, routing_enum):
        # type: (Live.Track.Track, AbstractEnum) -> None
        routing = find_if(lambda r: r.display_name == routing_enum.value,
                          getattr(track, self.available_routings_attribute_name))
        if not routing:
            raise Protocol0Error("couldn't find %s routing matching %s for %s" % (self.routing_attribute_name, routing_enum, track))
        setattr(track, self.routing_attribute_name, routing)
