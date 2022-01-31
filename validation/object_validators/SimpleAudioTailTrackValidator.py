from typing import Any

from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.validation.object_validators.SimpleAudioTrackValidator import SimpleAudioTrackValidator
from protocol0.validation.sub_validators.PropertyValueValidator import PropertyValueValidator


class SimpleAudioTailTrackValidator(SimpleAudioTrackValidator):
    def __init__(self, track, *a, **k):
        # type: (SimpleAudioTailTrack, Any, Any) -> None
        super(SimpleAudioTailTrackValidator, self).__init__(track, *a, **k)
        self._validators += [
            PropertyValueValidator(track.input_routing, "track", track.abstract_group_track.midi_track),
            PropertyValueValidator(track.input_routing, "channel",
                                   track.abstract_group_track.instrument.AUDIO_INPUT_ROUTING_CHANNEL),
        ]
        for clip in self._track.clips:
            self._validators.append(
                PropertyValueValidator(clip, "muted", True)
            )
