from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.routing.RoutingDescriptor import RoutingDescriptor
from protocol0.domain.lom.track.routing.RoutingTrackDescriptor import RoutingTrackDescriptor
from protocol0.domain.lom.track.routing.TrackRoutingInterface import TrackRoutingInterface


class TrackInputRouting(TrackRoutingInterface):
    type = RoutingDescriptor("input_routing_type", InputRoutingTypeEnum)
    track = RoutingTrackDescriptor("input_routing_type")
    channel = RoutingDescriptor("input_routing_channel", InputRoutingChannelEnum)
