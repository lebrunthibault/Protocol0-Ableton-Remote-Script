from typing import TYPE_CHECKING

from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, group_track, *a, **k):
        # type: (SimpleTrack) -> None
        super(AbstractGroupTrack, self).__init__(track=group_track, *a, **k)
        group_track.abstract_group_track = self
        self.sub_tracks = group_track.sub_tracks

        # tracks that are going to be mapped to this AbstractGroupTrack on selection
        # (that is their current track is self)
        self.selection_tracks = self.all_tracks
        # [setattr(sub_track, "base_color", self.base_color) for sub_track in self.sub_tracks]

    @p0_subject_slot("instrument")
    def _instrument_listener(self):
        self.instrument = self.instrument_track.instrument or self.base_track.instrument
        if self.instrument:
            self.instrument.track = self
