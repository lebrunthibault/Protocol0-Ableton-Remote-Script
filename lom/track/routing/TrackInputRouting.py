from typing import Any, Optional
from typing import TYPE_CHECKING

from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.track.routing.RoutingDescriptor import RoutingDescriptor
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class TrackInputRouting(AbstractObject):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(TrackInputRouting, self).__init__(*a, **k)
        self._track = track._track

    toto = RoutingDescriptor(InputRoutingTypeEnum, "input_routing_type")

    @property
    def track(self):
        # type: () -> Optional[SimpleTrack]
        if self._track.input_routing_type.attached_object:
            return self.parent.songTracksManager.get_simple_track(self._track.input_routing_type.attached_object)
        else:
            return None

    @track.setter
    def track(self, track):
        # type: (Optional[SimpleTrack]) -> None
        input_routing_type = find_if(lambda r: r.attached_object == track._track,
                                         self._track.available_input_routing_types)

        if not input_routing_type:
            raise Protocol0Error("Couldn't find the output routing type %s for %s" % (track, self))

        self._track.input_routing_type = input_routing_type

    @property
    def type(self):
        # type: () -> Optional[InputRoutingTypeEnum]
        try:
            return self._track and InputRoutingTypeEnum.from_value(self._track.input_routing_type.display_name)
        except Protocol0Error:
            return None

    @type.setter
    def type(self, input_routing_type_enum):
        # type: (InputRoutingTypeEnum) -> None
        input_routing_type = find_if(lambda i: i.display_name == input_routing_type_enum.label,
                                     self._track.available_input_routing_types)
        if input_routing_type is None:
            raise Protocol0Error("Couldn't find input routing type from %s for %s" % (input_routing_type_enum, self))
        self._track.input_routing_type = input_routing_type
