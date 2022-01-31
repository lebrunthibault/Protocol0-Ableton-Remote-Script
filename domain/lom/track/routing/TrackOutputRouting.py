from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.routing.RoutingDescriptor import RoutingDescriptor
from protocol0.domain.lom.track.routing.RoutingTrackDescriptor import RoutingTrackDescriptor
from protocol0.domain.lom.track.routing.TrackRoutingInterface import TrackRoutingInterface


class TrackOutputRouting(TrackRoutingInterface):
    type = RoutingDescriptor("output_routing_type", OutputRoutingTypeEnum)
    track = RoutingTrackDescriptor("output_routing_type")
