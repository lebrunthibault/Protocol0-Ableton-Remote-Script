from typing import TYPE_CHECKING

from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.utils.decorators import subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, group_track, *a, **k):
        # type: (SimpleTrack) -> None
        super(AbstractGroupTrack, self).__init__(track=group_track, *a, **k)
        self.sub_tracks = group_track.sub_tracks
        self.can_be_armed = True
        [setattr(sub_track, "base_color", self.base_color) for sub_track in self.sub_tracks]

    @subject_slot("instrument")
    def _instrument_listener(self):
        self.instrument = self.instrument_track.instrument or self.base_track.instrument
        if self.instrument:
            self.instrument.track = self
