from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.shared.BrowserManagerInterface import BrowserManagerInterface
from protocol0.shared.config import Config
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.instrument.instrument.InstrumentProphet import InstrumentProphet
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.lom.validation.object_validators.SimpleAudioTailTrackValidator import SimpleAudioTailTrackValidator
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.DeviceParameterValidator import DeviceParameterValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import PropertyValueValidator
from protocol0.domain.lom.validation.sub_validators.SimpleTrackHasDeviceValidator import SimpleTrackHasDeviceValidator


class ExternalSynthTrackValidator(AggregateValidator):
    def __init__(self, track, browser_manager):
        # type: (ExternalSynthTrack, BrowserManagerInterface) -> None
        self._track = track

        validators = [
            CallbackValidator(track, lambda t: t.instrument is not None, None, "track should have an instrument"),
            SimpleTrackHasDeviceValidator(track.midi_track, DeviceEnum.EXTERNAL_AUDIO_EFFECT, browser_manager),
            CallbackValidator(track.midi_track,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT) is None,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT).delete),
            PropertyValueValidator(track.midi_track, "volume", Config.ZERO_DB_VOLUME),  # 0 db
            PropertyValueValidator(track.audio_track, "volume", Config.ZERO_DB_VOLUME),

            # ROUTINGS

            PropertyValueValidator(track.midi_track.input_routing, "type", InputRoutingTypeEnum.REV2_AUX),
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

    def fix(self):
        # type: () -> Sequence
        self._track.monitoring_state.monitor_audio()
        seq = Sequence()
        seq.add(super(ExternalSynthTrackValidator, self).fix)
        seq.add(self._track.midi_track.select)
        return seq.done()
