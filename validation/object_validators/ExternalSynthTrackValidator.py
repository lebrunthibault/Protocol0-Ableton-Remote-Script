from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.utils.log import log_ableton
from protocol0.validation.AbstractObjectValidator import AbstractObjectValidator
from protocol0.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.validation.sub_validators.PropertyValidator import PropertyValidator
from protocol0.validation.sub_validators.SimpleTrackHasDeviceValidator import SimpleTrackHasDeviceValidator


class ExternalSynthTrackValidator(AbstractObjectValidator, AggregateValidator):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        self._track = track
        validators = [
            SimpleTrackHasDeviceValidator(track.midi_track, track.instrument.EXTERNAL_INSTRUMENT_DEVICE),
            PropertyValidator(track.midi_track, "input_routing_channel", InputRoutingChannelEnum.CHANNEL_1),
            PropertyValidator(track.audio_track, "input_routing_type", track.midi_track),
            PropertyValidator(track.audio_track, "input_routing_channel", track.instrument.AUDIO_INPUT_ROUTING_CHANNEL),
        ]
        self._validators = validators
        super(ExternalSynthTrackValidator, self).__init__(track)

    def is_valid(self):
        # type: () -> bool
        is_valid = super(ExternalSynthTrackValidator, self).is_valid()
        log_ableton("External instrument hardware latency should be %s" % self._track.instrument.EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY)
        return is_valid

    def notify_valid(self):
        # type: () -> None
        log_ableton("notify valid !")
        self._track.refresh_appearance()
