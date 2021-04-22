from typing import TYPE_CHECKING, Any

from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractGroupTrack, self).__init__(track=group_track, *a, **k)
        group_track.abstract_group_track = self
        self.sub_tracks = group_track.sub_tracks

        for sub_track in self.sub_tracks:
            sub_track.group_track = self

        # tracks that are going to be mapped to this AbstractGroupTrack on selection
        # (that is their current track is self)
        self.selection_tracks = self.all_tracks

    @p0_subject_slot("instrument")
    def _instrument_listener(self):
        # type: () -> None
        self.instrument = self.instrument_track.instrument or self.base_track.instrument
        self.instrument.sync_presets()
