import Live
from typing import Type, Any, Optional, TYPE_CHECKING

from protocol0.domain.lom.track.routing.TrackRoutingInterface import TrackRoutingInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import find_if
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class RoutingTrackDescriptor(object):
    def __init__(self, routing_attribute_name):
        # type: (str) -> None
        self.routing_attribute_name = routing_attribute_name
        self.available_routings_attribute_name = "available_%ss" % routing_attribute_name

    def __get__(self, track_routing, _):
        # type: (TrackRoutingInterface, Type) -> Optional[Any]
        track = getattr(track_routing._track, self.routing_attribute_name).attached_object
        if track:
            return SongFacade.simple_track_from_live_track(track)
        elif track_routing._track.output_routing_type.category == Live.Track.RoutingTypeCategory.parent_group_track:
            return SongFacade.simple_track_from_live_track(track_routing._track.group_track)
        else:
            return None

    def __set__(self, track_routing, track):
        # type: (TrackRoutingInterface, SimpleTrack) -> None
        available_routings = getattr(track_routing._track, self.available_routings_attribute_name)

        if track._track == track_routing._track.group_track:
            routing = find_if(lambda r: r.category == Live.Track.RoutingTypeCategory.parent_group_track,
                              available_routings)
        else:
            routing = find_if(lambda r: r.attached_object == track._track, available_routings)

            # still needed ?
            # if not routing:
            #     routing = find_if(lambda r: r.display_name == track.name, available_routings)

        if not routing:
            raise Protocol0Error("couldn't find %s routing matching %s for %s" % (
                self.routing_attribute_name,
                track._track.name,
                track_routing._track.name
            ))

        setattr(track_routing._track, self.routing_attribute_name, routing)
