from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator


class AbstractGroupTrackValidator(AggregateValidator):
    def __init__(self, _):
        # type: (AbstractGroupTrack) -> None
        super(AbstractGroupTrackValidator, self).__init__([])
