from typing import cast, List

from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import (
    SimpleAudioTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)


class SimpleAudioTailTrackValidator(SimpleAudioTrackValidator):
    def __init__(self, track, audio_track):
        # type: (SimpleAudioTailTrack, SimpleAudioExtTrack) -> None
        ext_track = cast(ExternalSynthTrack, track.abstract_group_track)
        validators = cast(
            List[ValidatorInterface],
            [
                PropertyValueValidator(
                    track.input_routing,
                    "track",
                    ext_track.midi_track,
                    name="tail track input track",
                ),
                PropertyValueValidator(
                    track.input_routing,
                    "channel",
                    InputRoutingChannelEnum.POST_FX,
                    name="tail track input channel",
                ),
            ],
        )
        for clip in track.clips:
            validators.append(PropertyValueValidator(clip, "muted", True))
            validators.append(PropertyValueValidator(clip.loop, "looping", False))
            audio_clip = audio_track.clip_slots[clip.index].clip
            assert audio_clip, "Got audio tail clip without audio clip"
            validators.append(
                PropertyValueValidator(
                    clip.loop,
                    "bar_length",
                    audio_clip.loop.bar_length,
                    "%s should have the same bar_length as %s" % (clip, audio_clip),
                    fix=False
                )
            )

        super(SimpleAudioTailTrackValidator, self).__init__(track, validators=validators)
