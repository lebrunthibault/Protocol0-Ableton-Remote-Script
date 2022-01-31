from typing import Any, Optional
from typing import TYPE_CHECKING

import Live

from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class TrackOutputRouting(AbstractObject):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(TrackOutputRouting, self).__init__(*a, **k)
        self._track = track._track
        self._group_track = track.group_track

    @property
    def track(self):
        # type: () -> Optional[SimpleTrack]
        if self._track and self._track.output_routing_type.attached_object:
            return self.parent.songTracksManager.get_simple_track(self._track.output_routing_type.attached_object)
        elif self._track.output_routing_type.category == Live.Track.RoutingTypeCategory.parent_group_track:
            return self._group_track
        elif self._track.output_routing_type.category == Live.Track.RoutingTypeCategory.master:
            return self.song.master_track
        else:
            return None

    @track.setter
    def track(self, track):
        # type: (SimpleTrack) -> None
        if self._track is None:
            return
        output_routing_type = find_if(lambda r: r.attached_object == track._track, self._track.available_output_routing_types)

        if not output_routing_type:
            output_routing_type = find_if(lambda r: r.display_name == track.name, self._track.available_output_routing_types)

        if not output_routing_type:
            raise Protocol0Error("Couldn't find the output routing type %s for %s" % (track, self))

        self._track.output_routing_type = output_routing_type
