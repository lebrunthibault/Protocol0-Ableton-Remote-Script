from typing import Optional

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.validation.object_validators.SimpleAudioTailTrackValidator import \
    SimpleAudioTailTrackValidator
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import \
    SimpleAudioTrackValidator
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import \
    PropertyValueValidator
from protocol0.domain.lom.validation.sub_validators.SimpleTrackHasDeviceValidator import \
    SimpleTrackHasDeviceValidator
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrackValidator(AggregateValidator):
    def __init__(self, track, browser_service):
        # type: (ExternalSynthTrack, BrowserServiceInterface) -> None
        self._track = track

        validators = [
            # INSTRUMENT AND DEVICES
            CallbackValidator(track, lambda t: t.instrument is not None, None, "track should have an instrument"),
            SimpleTrackHasDeviceValidator(track.midi_track, DeviceEnum.EXTERNAL_AUDIO_EFFECT, browser_service),
            CallbackValidator(track.midi_track,
                              lambda t: t.devices.get_one_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT) is None),

            # VOLUMES
            PropertyValueValidator(track.midi_track, "volume", 0, name="midi track volume"),
            PropertyValueValidator(track.audio_track, "volume", 0, name="audio track volume"),

            # ROUTINGS
            CallbackValidator(track, lambda t: t.midi_track.input_routing.type in (
                InputRoutingTypeEnum.ALL_INS,
                InputRoutingTypeEnum.REV2_AUX
            ), None, "midi track input type"),
            PropertyValueValidator(track.midi_track.input_routing, "channel", InputRoutingChannelEnum.CHANNEL_1,
                                   name="midi track input channel"),
            PropertyValueValidator(track.audio_track.input_routing, "track",
                                   track.midi_track,
                                   name="audio track input track"),
            PropertyValueValidator(track.audio_track.input_routing, "channel", InputRoutingChannelEnum.POST_FX,
                                   name="audio track input channel"),
        ]

        # SUB TRACKS
        validators += SimpleAudioTrackValidator(track.audio_track)._validators

        if track.audio_tail_track:
            validators += SimpleAudioTailTrackValidator(track.audio_tail_track)._validators

        if len(track.dummy_tracks) == 0 and not track.is_armed:
            validators.append(PropertyValueValidator(track.audio_track.output_routing, "track", track.base_track,
                                                     name="audio track output routing"))
            if track.audio_tail_track:
                validators.append(
                    PropertyValueValidator(track.audio_tail_track.output_routing, "track", track.base_track,
                                           name="tail track output routing"))

        for dummy_track in track.dummy_tracks:
            validators += [
                PropertyValueValidator(dummy_track, "volume", 0),
                PropertyValueValidator(dummy_track, "current_monitoring_state", CurrentMonitoringStateEnum.IN)
                ]

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
