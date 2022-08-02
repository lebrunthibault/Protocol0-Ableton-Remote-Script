from typing import Optional, List

from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.AbstractGroupTrackValidator import (
    AbstractGroupTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyReturnTrackValidator import (
    SimpleDummyReturnTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyTrackValidator import (
    SimpleDummyTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleAudioExtTrackValidator import \
    SimpleAudioExtTrackValidator
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleAudioTailTrackValidator import (
    SimpleAudioTailTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleMidiExtTrackValidator import \
    SimpleMidiExtTrackValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrackValidator(AbstractGroupTrackValidator):
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

        # AUDIO TAIL TRACK
        # always preset except for Minitaur (mono)
        validators.append(CallbackValidator(
            track,
            lambda t: isinstance(t.instrument, InstrumentMinitaur) or t.audio_tail_track is not None,
            None,
            "track should have an audio tail track",
        ))
        if track.audio_tail_track:
            validators += SimpleAudioTailTrackValidator(track.audio_tail_track)._validators

        # DUMMY TRACK ROUTINGS
        if track.dummy_track is None and not track.is_armed:
            validators.append(
                PropertyValueValidator(
                    track.audio_track.output_routing,
                    "track",
                    track.base_track,
                    name="audio track output routing",
                )
            )
            if track.audio_tail_track:
                validators.append(
                    PropertyValueValidator(
                        track.audio_tail_track.output_routing,
                        "track",
                        track.base_track,
                        name="tail track output routing",
                    )
                )
        # DUMMY TRACK
        if track.dummy_track is not None:
            validators.append(SimpleDummyTrackValidator(track.dummy_track))

        # DUMMY RETURN TRACK
        if track.dummy_return_track is not None:
            validators.append(SimpleDummyReturnTrackValidator(track.dummy_return_track))

        super(ExternalSynthTrackValidator, self).__init__(track, validators)

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
