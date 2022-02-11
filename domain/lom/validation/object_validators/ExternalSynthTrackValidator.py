from typing import Optional

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.instrument.instrument.InstrumentProphet import InstrumentProphet
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.validation.object_validators.SimpleAudioTailTrackValidator import \
    SimpleAudioTailTrackValidator
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.DeviceParameterValidator import DeviceParameterValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import PropertyValueValidator
from protocol0.domain.lom.validation.sub_validators.SimpleTrackHasDeviceValidator import SimpleTrackHasDeviceValidator
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.Config import Config
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrackValidator(AggregateValidator):
    def __init__(self, track, browser_service):
        # type: (ExternalSynthTrack, BrowserServiceInterface) -> None
        self._track = track

        validators = [
            CallbackValidator(track, lambda t: t.instrument is not None, None, "track should have an instrument"),
            SimpleTrackHasDeviceValidator(track.midi_track, DeviceEnum.EXTERNAL_AUDIO_EFFECT, browser_service),
            CallbackValidator(track.midi_track,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT) is None,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT).delete),
            PropertyValueValidator(track.midi_track, "volume", Config.ZERO_DB_VOLUME),  # 0 db
            PropertyValueValidator(track.audio_track, "volume", Config.ZERO_DB_VOLUME),

            # ROUTINGS

            PropertyValueValidator(track.midi_track.input_routing, "type", track.instrument.MIDI_INPUT_ROUTING_TYPE),
            PropertyValueValidator(track.audio_track.input_routing, "track", track.midi_track),
            PropertyValueValidator(track.audio_track.input_routing, "channel", InputRoutingChannelEnum.POST_FX),
        ]

        if track.audio_tail_track:
            validators += SimpleAudioTailTrackValidator(track.audio_tail_track)._validators

        if len(track.dummy_tracks) == 0:
            validators += [
                PropertyValueValidator(track.midi_track.output_routing, "track", track.base_track),
                PropertyValueValidator(track.audio_track.output_routing, "track", track.base_track),
            ]
            if track.audio_tail_track:
                validators.append(PropertyValueValidator(track.audio_tail_track.output_routing, "track", track.base_track))

        for dummy_track in track.dummy_tracks:
            validators.append(PropertyValueValidator(dummy_track, "volume", Config.ZERO_DB_VOLUME))

        instrument = track.instrument
        if isinstance(instrument, InstrumentProphet):
            validators.append(DeviceParameterValidator(instrument.device, DeviceParameterEnum.DEVICE_ON, instrument.EDITOR_DEVICE_ON))

        super(ExternalSynthTrackValidator, self).__init__(validators)

    def get_error_message(self):
        # type: () -> Optional[str]
        error_message = super(ExternalSynthTrackValidator, self).get_error_message()
        if error_message:
            return "Error on %s. %s" % (self._track, error_message)
        return error_message

    def fix(self):
        # type: () -> Sequence
        self._track.monitoring_state.monitor_audio()
        seq = Sequence()
        seq.add(super(ExternalSynthTrackValidator, self).fix)
        seq.add(self._track.midi_track.select)
        return seq.done()
