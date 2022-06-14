import Live
from typing import Type, Any, Optional

from protocol0.domain.lom.track.P0TrackInterface import P0TrackInterface
from protocol0.domain.lom.track.routing.TrackRoutingInterface import TrackRoutingInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.utils import find_if
from protocol0.shared.SongFacade import SongFacade


class RoutingTrackDescriptor(object):
    def __init__(self, routing_attribute_name):
        # type: (str) -> None
        self.routing_attribute_name = routing_attribute_name
        self.available_routings_attribute_name = "available_%ss" % routing_attribute_name

    def __get__(self, track_routing, _):
        # type: (TrackRoutingInterface, Type) -> Optional[Any]
        track = getattr(track_routing.live_track, self.routing_attribute_name).attached_object
        if track:
            return SongFacade.simple_track_from_live_track(track)
        elif track_routing.live_track.output_routing_type.category == Live.Track.RoutingTypeCategory.parent_group_track:
            return SongFacade.simple_track_from_live_track(track_routing.live_track.group_track)
        else:
            return None

    # noinspection PyShadowingNames
    def __set__(self, track_routing, track):
        # type: (TrackRoutingInterface, P0TrackInterface) -> None
        live_track = track._track
        available_routings = getattr(track_routing.live_track, self.available_routings_attribute_name)
        routing = None

        # NB : for input routings a group track doesn't have this shortcut routing
        if live_track == track_routing.live_track.group_track:
            routing = find_if(lambda r: r.category == Live.Track.RoutingTypeCategory.parent_group_track,
                              available_routings)
        if routing is None:
            routing = find_if(lambda r: r.attached_object == live_track, available_routings)

            # still needed ?
            # if not routing:
            #     routing = find_if(lambda r: r.display_name == track.name, available_routings)

        if not routing:
            raise Protocol0Error("couldn't find %s routing matching %s for %s. Available routings are : %s" % (
                self.routing_attribute_name,
                live_track.name,
                track_routing.live_track.name,
                [(r.category, r.display_name) for r in available_routings]
            ))

        setattr(track_routing.live_track, self.routing_attribute_name, routing)
