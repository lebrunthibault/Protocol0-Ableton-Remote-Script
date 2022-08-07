from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator


class SimpleTrackValidator(AggregateValidator):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        self._track = track
        # nothing done here
        super(SimpleTrackValidator, self).__init__([])
