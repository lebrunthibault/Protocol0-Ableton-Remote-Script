from typing import TYPE_CHECKING

from _Framework.Util import find_if
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, group_track, *a, **k):
        # type: (SimpleTrack) -> None
        super(AbstractGroupTrack, self).__init__(track=group_track, *a, **k)
        self.sub_tracks = group_track.sub_tracks
        self.can_be_armed = True
        # no error handling here, this is a critical
        instrument_track = find_if(lambda t: t.instrument, [group_track] + self.sub_tracks)  # type: SimpleTrack
        if instrument_track:
            self.instrument = instrument_track.instrument
            self.instrument.track = self
        [setattr(sub_track, "base_color", self.base_color) for sub_track in self.sub_tracks]
