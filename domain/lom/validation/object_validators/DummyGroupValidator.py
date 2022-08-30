from functools import partial

from typing import Optional, List, TYPE_CHECKING

from protocol0.domain.lom.clip.DummyClip import DummyClip
from protocol0.domain.lom.track.simple_track.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyReturnTrackValidator import (
    SimpleDummyReturnTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyTrackValidator import (
    SimpleDummyTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)
from protocol0.shared.SongFacade import SongFacade

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

        # check that there is no lone dummy clips in the track
        for scene in SongFacade.scenes():
            validators.append(
                CallbackValidator(
                    group_track,
                    partial(self._track_has_lone_dummy_clips_validator, scene_index=scene.index),
                    None,
                    "%s has lone dummy clips on scene %s" % (group_track, scene),
                )
            )

        super(DummyGroupValidator, self).__init__(validators)

    def _track_has_lone_dummy_clips_validator(self, track, scene_index):
        # type: (AbstractGroupTrack, int) -> bool
        clips = filter(None, [track.clip_slots[scene_index].clip for track in track.sub_tracks])
        return len(clips) == 0 or any(not isinstance(clip, DummyClip) for clip in clips)
