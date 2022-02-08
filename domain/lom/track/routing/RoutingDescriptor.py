from typing import Type, Any, Optional

from protocol0.domain.enums.AbstractEnum import AbstractEnum
from protocol0.domain.lom.track.routing.TrackRoutingInterface import TrackRoutingInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import find_if


class RoutingDescriptor(object):
    def __init__(self, routing_attribute_name, routing_enum_class):
        # type: (str, Type[AbstractEnum]) -> None
        self.routing_enum_class = routing_enum_class
        self.routing_attribute_name = routing_attribute_name
        self.available_routings_attribute_name = "available_%ss" % routing_attribute_name

    def __get__(self, track_routing, _):
        # type: (TrackRoutingInterface, Type) -> Optional[Any]
        try:
            return self.routing_enum_class.from_value(getattr(track_routing._track, self.routing_attribute_name).display_name)
        except Protocol0Error:
            return None

    def __set__(self, track_routing, routing_enum):
        # type: (TrackRoutingInterface, AbstractEnum) -> None
        routing = find_if(lambda r: r.display_name == routing_enum.value,
                          getattr(track_routing._track, self.available_routings_attribute_name))
        if not routing:
            raise Protocol0Error("couldn't find %s routing matching %s for %s" % (self.routing_attribute_name, routing_enum, track_routing._track))
        setattr(track_routing._track, self.routing_attribute_name, routing)
