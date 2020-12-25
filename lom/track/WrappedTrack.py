from typing import TYPE_CHECKING

from _Framework.Util import find_if, forward_property
from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class WrappedTrack(ExternalSynthTrackActionMixin, AbstractTrack):
    def __init__(self, track, wrapped_track, *a, **k):
        # type: (SimpleTrack, SimpleTrack) -> None
        super(WrappedTrack, self).__init__(track=track._track, *a, **k)
        self.base_track = track
        self.wrapped_track = wrapped_track
        self.group_track = self.base_track.group_track
        self.group_tracks = self.base_track.group_track
        self.sub_tracks = self.base_track.sub_tracks
        self.midi = self.sub_tracks[0]
        self.audio = self.sub_tracks[1]
        self.can_be_armed = True
        if not self.arm:
            self.is_folded = True

        # no error handling here, this is a critical
        self.instrument = find_if(lambda t: t.instrument, [self.base_track] + self.sub_tracks).instrument  # type: AbstractInstrument
        self.instrument.track = self
        [setattr(sub_track, "base_color", self.base_color) for sub_track in self.sub_tracks]

    @forward_property('wrapped_track')
    def arm(): pass

    @forward_property('wrapped_track')
    def is_playing(): pass

    @forward_property('wrapped_track')
    def is_recording(): pass

    @forward_property('wrapped_track')
    def next_empty_clip_slot_index(): pass
