from typing import Type, Any, Optional, TYPE_CHECKING

from protocol0 import Protocol0
from protocol0.enums.AbstractEnum import AbstractEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
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

        track = getattr(track._track, self.routing_attribute_name).attached_object
        if track:
            return Protocol0.SELF.songTracksManager.get_simple_track(track)
        else:
            return None

    def __set__(self, r, track):
        # type: (TrackInputRouting, SimpleTrack) -> None
        routing = find_if(lambda r: r.attached_object == track._track,
                          getattr(r._track, self.available_routings_attribute_name))

        if not routing:
            raise Protocol0Error("couldn't find %s routing matching %s for %s" % (self.routing_attribute_name, track._track, r._track))

        setattr(track, self.routing_attribute_name, routing)
