from typing import Optional, List

from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleAudioExtTrackValidator import (
    SimpleAudioExtTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleMidiExtTrackValidator import (
    SimpleMidiExtTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrackValidator(AggregateValidator):
    def __init__(self, track, browser_service):
        # type: (ExternalSynthTrack, BrowserServiceInterface) -> None
        self._track = track

        validators = [
            CallbackValidator(
                track, lambda t: t.instrument is not None, None, "track should have an instrument"
            ),
        ]  # type: List[ValidatorInterface]

        # SUB TRACKS
        validators += SimpleMidiExtTrackValidator(track.midi_track, browser_service)._validators
        validators += SimpleAudioExtTrackValidator(track.audio_track, track.midi_track)._validators

        super(ExternalSynthTrackValidator, self).__init__(validators)

    def get_error_message(self):
        # type: () -> Optional[str]
        error_message = super(ExternalSynthTrackValidator, self).get_error_message()
        if error_message:
            return "%s -> %s" % (self._track, error_message)
        return error_message

    def fix(self):
        # type: () -> Sequence
        self._track.monitoring_state.monitor_audio()
        seq = Sequence()
        seq.add(super(ExternalSynthTrackValidator, self).fix)
        return seq.done()
