from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.routing.RoutingDisplayNameDescriptor import (
    RoutingDisplayNameDescriptor,
)
from protocol0.domain.lom.track.routing.RoutingTrackDescriptor import RoutingTrackDescriptor
from protocol0.domain.lom.track.routing.TrackRoutingInterface import TrackRoutingInterface


class TrackOutputRouting(TrackRoutingInterface):
    type = RoutingDisplayNameDescriptor("output_routing_type", OutputRoutingTypeEnum)
    track = RoutingTrackDescriptor("output_routing_type")
