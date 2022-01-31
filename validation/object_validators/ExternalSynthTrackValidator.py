from typing import Any

from protocol0.config import Config
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.DeviceParameterEnum import DeviceParameterEnum
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.validation.AbstractObjectValidator import AbstractObjectValidator
from protocol0.validation.object_validators.SimpleAudioTailTrackValidator import SimpleAudioTailTrackValidator
from protocol0.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.validation.sub_validators.DeviceParameterValidator import DeviceParameterValidator
from protocol0.validation.sub_validators.PropertyValueValidator import PropertyValueValidator
from protocol0.validation.sub_validators.SimpleTrackHasDeviceValidator import SimpleTrackHasDeviceValidator


class ExternalSynthTrackValidator(AbstractObjectValidator, AggregateValidator):
    def __init__(self, track, *a, **k):
        # type: (ExternalSynthTrack, Any, Any) -> None
        self._track = track

        validators = [
            CallbackValidator(track, lambda t: t.instrument is not None, None, "track should have an instrument"),
            SimpleTrackHasDeviceValidator(track.midi_track, track.instrument.EXTERNAL_INSTRUMENT_DEVICE),
            CallbackValidator(track.midi_track,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT) is None,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT).delete),
            PropertyValueValidator(track.midi_track, "volume", Config.ZERO_DB_VOLUME),  # 0 db
            PropertyValueValidator(track.audio_track, "volume", Config.ZERO_DB_VOLUME),

            # ROUTINGS

            # PropertyValueValidator(track.output_routing, "track", Protocol0.SELF.protocol0_song.master_track),
            PropertyValueValidator(track.midi_track.input_routing, "type", track.instrument.MIDI_INPUT_ROUTING_TYPE),
            # PropertyValueValidator(track.midi_track.input_routing, "channel", InputRoutingChannelEnum.CHANNEL_1),
            PropertyValueValidator(track.audio_track.input_routing, "track", track.midi_track),
            PropertyValueValidator(track.audio_track.input_routing, "channel",
                                   track.instrument.AUDIO_INPUT_ROUTING_CHANNEL),
        ]

        if track.audio_tail_track:
            validators += SimpleAudioTailTrackValidator(track.audio_tail_track, *a, **k)._validators

        if len(track.dummy_tracks) == 0:
            validators += [
                PropertyValueValidator(track.midi_track.output_routing, "track", track.base_track),
                PropertyValueValidator(track.audio_track.output_routing, "track", track.base_track),
            ]
            if track.audio_tail_track:
                validators.append(PropertyValueValidator(track.audio_tail_track.output_routing, "track", track.base_track))

        for dummy_track in track.dummy_tracks:
            validators.append(PropertyValueValidator(dummy_track, "volume", Config.ZERO_DB_VOLUME))

        if track.instrument.device:
            validators.append(DeviceParameterValidator(track.instrument.device, DeviceParameterEnum.DEVICE_ON, False))
        self._validators = validators
        super(ExternalSynthTrackValidator, self).__init__(track, *a, **k)

    def is_valid(self):
        # type: () -> bool
        is_valid = super(ExternalSynthTrackValidator, self).is_valid()
        self.log(
            "External instrument hardware latency should be %s" % self._track.instrument.EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY)
        return is_valid

    def fix(self):
        # type: () -> Sequence
        self._track.monitoring_state.monitor_audio()
        seq = Sequence()
        seq.add(super(ExternalSynthTrackValidator, self).fix)
        seq.add(self._track.midi_track.select)
        return seq.done()
