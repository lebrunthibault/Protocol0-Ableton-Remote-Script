from typing import Optional, List, TYPE_CHECKING

from protocol0.domain.lom.track.simple_track.audio.dummy.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.audio.dummy.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyReturnTrackValidator import (
    SimpleDummyReturnTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyTrackValidator import (
    SimpleDummyTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class DummyGroupValidator(AggregateValidator):
    def __init__(self, group_track, dummy_track, dummy_return_track):
        # type: (AbstractGroupTrack, Optional[SimpleDummyTrack], Optional[SimpleDummyReturnTrack]) -> None
        validators = []  # type: List[ValidatorInterface]

        for sub_track in group_track.sub_tracks:
            if not isinstance(sub_track, (SimpleDummyTrack, SimpleMidiExtTrack)):
                validators.append(
                    PropertyValueValidator(
                        sub_track.output_routing,
                        "track",
                        dummy_track or group_track.base_track,
                        name="track output routing",
                    ),
                )

        # DUMMY TRACK
        if dummy_track is not None:
            validators.append(SimpleDummyTrackValidator(dummy_track))

        # DUMMY RETURN TRACK
        if dummy_return_track is not None:
            validators.append(SimpleDummyReturnTrackValidator(dummy_return_track))

        super(DummyGroupValidator, self).__init__(validators)
