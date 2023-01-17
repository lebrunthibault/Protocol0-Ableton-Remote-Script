from typing import cast, List

from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import (
    SimpleAudioTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)
from protocol0.shared.Config import Config


class SimpleAudioTailTrackValidator(SimpleAudioTrackValidator):
    def __init__(self, track):
        # type: (SimpleAudioTailTrack) -> None
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
            validators.append(PropertyValueValidator(clip, "warp_mode", Config.DEFAULT_WARP_MODE))

            audio_clip = ext_track.audio_track.clip_slots[clip.index].clip

            if audio_clip is None:
                validators.append(
                    CallbackValidator(
                        track,
                        lambda c: False,
                        None,
                        "Got audio tail clip without audio clip for %s at scene %s"
                        % (ext_track, clip.index),
                    )
                )

                continue

            if audio_clip.bar_length != clip.bar_length:
                validators.append(
                    CallbackValidator(
                        track,
                        lambda c: False,
                        self._fix_clip_lengths,
                        "%s should have the same bar_length as %s" % (clip, audio_clip),
                    ),
                )

        super(SimpleAudioTailTrackValidator, self).__init__(track, validators=validators)

    def _fix_clip_lengths(self, track):
        # type: (SimpleAudioTailTrack) -> None
        audio_track = cast(ExternalSynthTrack, track.abstract_group_track).audio_track
        for clip in track.clips:
            audio_clip = audio_track.clip_slots[clip.index].clip
            if audio_clip.bar_length != clip.bar_length:
                # when this happens it always means one is shorter
                # (e.g. the prepare for scrub was not reset)
                bar_length = max(audio_clip.bar_length, clip.bar_length)
                audio_clip.bar_length = bar_length
                clip.bar_length = bar_length
